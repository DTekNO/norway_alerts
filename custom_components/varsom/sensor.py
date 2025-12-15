"""Varsom Alerts sensor platform."""
import asyncio
import logging
from datetime import timedelta

import aiohttp
import voluptuous as vol

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN,
    CONF_LANG,
    CONF_COUNTY_ID,
    CONF_COUNTY_NAME,
    CONF_WARNING_TYPE,
    CONF_MUNICIPALITY_FILTER,
    API_BASE_LANDSLIDE,
    API_BASE_FLOOD,
    WARNING_TYPE_LANDSLIDE,
    WARNING_TYPE_FLOOD,
    WARNING_TYPE_BOTH,
    ACTIVITY_LEVEL_NAMES,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=30)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Varsom Alerts sensor from a config entry."""
    # Get config from entry.options (preferred) or entry.data (fallback)
    # Options are used when user updates config, data is from initial setup
    config = entry.options if entry.options else entry.data
    
    county_id = config.get(CONF_COUNTY_ID) or entry.data.get(CONF_COUNTY_ID)
    county_name = config.get(CONF_COUNTY_NAME) or entry.data.get(CONF_COUNTY_NAME, "Unknown")
    warning_type = config.get(CONF_WARNING_TYPE) or entry.data.get(CONF_WARNING_TYPE)
    lang = config.get(CONF_LANG) or entry.data.get(CONF_LANG, "en")
    municipality_filter = config.get(CONF_MUNICIPALITY_FILTER, "")
    
    coordinator = VarsomAlertsCoordinator(hass, county_id, county_name, warning_type, lang)
    await coordinator.async_config_entry_first_refresh()
    
    # Create single sensor with all alerts in attributes
    entities = [
        VarsomAlertsSensor(coordinator, entry.entry_id, county_name, warning_type, municipality_filter),
    ]
    async_add_entities(entities)


class VarsomAlertsCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Varsom Alerts data."""

    def __init__(self, hass, county_id, county_name, warning_type, lang):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.county_id = county_id
        self.county_name = county_name
        self.warning_type = warning_type
        self.lang = lang

    async def _fetch_warnings(self, base_url: str, danger_type_label: str):
        """Fetch warnings from a specific API endpoint."""
        url = f"{base_url}/Warning/County/{self.county_id}/{self.lang}"
        headers = {
            "Accept": "application/json",
            "User-Agent": "varsom/1.0.0 jeremy.m.cook@gmail.com"
        }
        
        _LOGGER.debug("Fetching %s warnings from: %s", danger_type_label, url)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with asyncio.timeout(10):
                    async with session.get(url, headers=headers) as response:
                        if response.status != 200:
                            _LOGGER.error("Error fetching %s data: %s", danger_type_label, response.status)
                            return []

                        content_type = response.headers.get("Content-Type", "")
                        if "application/json" not in content_type:
                            _LOGGER.error("Unexpected Content-Type for %s: %s", danger_type_label, content_type)
                            return []

                        json_data = await response.json()
                        _LOGGER.info("Successfully fetched %s warnings (count: %d)", danger_type_label, len(json_data))
                        return json_data
                        
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching %s warnings: %s", danger_type_label, err)
            return []
        except Exception as err:
            _LOGGER.error("Unexpected error fetching %s warnings: %s", danger_type_label, err)
            return []

    async def _async_update_data(self):
        """Fetch data from API."""
        all_warnings = []
        
        try:
            # Fetch landslide warnings
            if self.warning_type in [WARNING_TYPE_LANDSLIDE, WARNING_TYPE_BOTH]:
                landslide_warnings = await self._fetch_warnings(API_BASE_LANDSLIDE, "landslide")
                for warning in landslide_warnings:
                    warning["_warning_type"] = "landslide"
                all_warnings.extend(landslide_warnings)
            
            # Fetch flood warnings
            if self.warning_type in [WARNING_TYPE_FLOOD, WARNING_TYPE_BOTH]:
                flood_warnings = await self._fetch_warnings(API_BASE_FLOOD, "flood")
                for warning in flood_warnings:
                    warning["_warning_type"] = "flood"
                all_warnings.extend(flood_warnings)
            
            _LOGGER.info("Total warnings fetched: %d", len(all_warnings))
            return all_warnings
            
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")


class VarsomAlertsSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Varsom Alerts sensor with all alerts in attributes."""

    def __init__(self, coordinator: VarsomAlertsCoordinator, entry_id: str, county_name: str, warning_type: str, municipality_filter: str = ""):
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        # Create sensor name based on warning type
        warning_type_label = warning_type.replace("_", " ").title()
        self._attr_name = f"Varsom {warning_type_label} {county_name}"
        self._attr_unique_id = f"{entry_id}_alerts"
        self._attr_has_entity_name = False
        self._county_name = county_name
        self._warning_type = warning_type
        self._municipality_filter = municipality_filter.strip()
    
    def _filter_alerts(self, alerts):
        """Filter alerts by municipality if filter is set."""
        if not self._municipality_filter:
            _LOGGER.debug("No municipality filter set, returning all %d alerts", len(alerts))
            return alerts
        
        _LOGGER.info("Filtering %d alerts with municipality filter: '%s'", len(alerts), self._municipality_filter)
        
        # Split filter by comma for multiple municipalities
        filter_terms = [term.strip().lower() for term in self._municipality_filter.split(",")]
        _LOGGER.debug("Filter terms: %s", filter_terms)
        
        filtered = []
        for alert in alerts:
            municipalities = alert.get("MunicipalityList", [])
            muni_names = [m.get("Name", "").lower() for m in municipalities]
            
            _LOGGER.debug("Checking alert ID %s with municipalities: %s", alert.get("Id"), muni_names)
            
            # Check if any municipality matches any filter term
            matches = False
            for filter_term in filter_terms:
                for muni_name in muni_names:
                    if filter_term in muni_name:
                        matches = True
                        _LOGGER.debug("  -> MATCH: '%s' in '%s'", filter_term, muni_name)
                        break
                if matches:
                    break
            
            if matches:
                filtered.append(alert)
            else:
                _LOGGER.debug("  -> NO MATCH for alert ID %s", alert.get("Id"))
        
        _LOGGER.info("Filtered to %d alerts matching '%s'", len(filtered), self._municipality_filter)
        return filtered

    @property
    def native_value(self):
        """Return the state of the sensor (highest activity level)."""
        if not self.coordinator.data:
            return "1"  # Green - no alerts
        
        # Apply municipality filter if set
        filtered_data = self._filter_alerts(self.coordinator.data)
        
        # Filter out green level (1) alerts
        active_alerts = [
            alert for alert in filtered_data
            if alert.get("ActivityLevel", "1") != "1"
        ]
        
        if not active_alerts:
            return "1"  # Green - no active warnings
        
        # Find highest activity level
        max_level = max(int(alert.get("ActivityLevel", "1")) for alert in active_alerts)
        return str(max_level)

    @property
    def extra_state_attributes(self):
        """Return the state attributes with all alerts."""
        if not self.coordinator.data:
            return {
                "active_alerts": 0,
                "highest_level": "green",
                "highest_level_numeric": 1,
                "alerts": [],
                "county_name": self._county_name,
                "county_id": self.coordinator.county_id,
                "municipality_filter": self._municipality_filter,
            }
        
        # Apply municipality filter if set
        filtered_data = self._filter_alerts(self.coordinator.data)
        
        # Filter out green level (1) alerts
        active_alerts = [
            alert for alert in filtered_data
            if alert.get("ActivityLevel", "1") != "1"
        ]
        
        # Determine highest level
        if active_alerts:
            max_level = max(int(alert.get("ActivityLevel", "1")) for alert in active_alerts)
        else:
            max_level = 1
        
        # Build alerts array
        alerts_list = []
        for alert in active_alerts:
            forecast_id = alert.get("Id", "")
            activity_level = alert.get("ActivityLevel", "1")
            
            # Construct varsom.no URL
            lang_path = "en" if self.coordinator.lang == "en" else ""
            varsom_url = f"https://www.varsom.no/{lang_path}/flood-and-landslide-warning-service/forecastid/{forecast_id}".replace("//f", "/f") if forecast_id else None
            
            # Get municipality list
            municipalities = [m.get("Name", "") for m in alert.get("MunicipalityList", [])]
            
            alert_dict = {
                "id": forecast_id,
                "level": int(activity_level),
                "level_name": ACTIVITY_LEVEL_NAMES.get(activity_level, "unknown"),
                "danger_type": alert.get("DangerTypeName", ""),
                "warning_type": alert.get("_warning_type", "unknown"),
                "municipalities": municipalities,
                "valid_from": alert.get("ValidFrom", ""),
                "valid_to": alert.get("ValidTo", ""),
                "danger_increases": alert.get("DangerIncreaseDateTime"),
                "danger_decreases": alert.get("DangerDecreaseDateTime"),
                "main_text": alert.get("MainText", ""),
                "warning_text": alert.get("WarningText", ""),
                "advice_text": alert.get("AdviceText", ""),
                "consequence_text": alert.get("ConsequenceText", ""),
                "url": varsom_url,
            }
            alerts_list.append(alert_dict)
        
        # Sort by level (highest first)
        alerts_list.sort(key=lambda x: x["level"], reverse=True)
        
        return {
            "active_alerts": len(alerts_list),
            "highest_level": ACTIVITY_LEVEL_NAMES.get(str(max_level), "green"),
            "highest_level_numeric": max_level,
            "alerts": alerts_list,
            "county_name": self._county_name,
            "county_id": self.coordinator.county_id,
            "municipality_filter": self._municipality_filter,
        }

    @property
    def icon(self):
        """Return the icon based on the highest alert level."""
        state = self.native_value
        if state == "4":
            return "mdi:alert-octagon"  # Red
        elif state == "3":
            return "mdi:alert"  # Orange
        elif state == "2":
            return "mdi:alert-circle"  # Yellow
        else:
            return "mdi:check-circle"  # Green
