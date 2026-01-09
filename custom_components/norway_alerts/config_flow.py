"""Config flow for Varsom Alerts integration."""
import asyncio
import logging

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_LANG,
    DEFAULT_WARNING_TYPE,
    CONF_LANG,
    CONF_COUNTY_ID,
    CONF_COUNTY_NAME,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_WARNING_TYPE,
    CONF_MUNICIPALITY_FILTER,
    CONF_TEST_MODE,
    CONF_ENABLE_NOTIFICATIONS,
    CONF_NOTIFICATION_SEVERITY,
    API_BASE_LANDSLIDE,
    API_BASE_AVALANCHE,
    COUNTIES,
    WARNING_TYPE_LANDSLIDE,
    WARNING_TYPE_FLOOD,
    WARNING_TYPE_AVALANCHE,
    WARNING_TYPE_METALERTS,
    NOTIFICATION_SEVERITIES,
    NOTIFICATION_SEVERITY_YELLOW_PLUS,
)

_LOGGER = logging.getLogger(__name__)


async def validate_api_connection(hass: HomeAssistant, county_id: str, warning_type: str, lang: str):
    """Validate that the API connection works."""
    # Test with landslide API for county-based warnings (always available)
    # Note: Avalanche API uses different structure (regions instead of counties)
    # but we still validate against landslide API for basic connectivity
    url = f"{API_BASE_LANDSLIDE}/Warning/County/{county_id}/{lang}"
    headers = {
        "Accept": "application/json",
        "User-Agent": "varsom/1.0.0 jeremy.m.cook@gmail.com"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with asyncio.timeout(10):
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        raise ValueError(f"API returned status {response.status}")
                    
                    content_type = response.headers.get('Content-Type', '')
                    if 'application/json' not in content_type:
                        raise ValueError(f"Unexpected content type: {content_type}")
                    
                    # Try to parse JSON
                    await response.json()
                    return True
    except aiohttp.ClientError as err:
        raise ValueError(f"Cannot connect to API: {err}")
    except Exception as err:
        raise ValueError(f"Unexpected error: {err}")


class VarsomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Varsom Alerts."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step - select warning type."""
        errors = {}

        if user_input is not None:
            # Store warning type selection
            warning_type = user_input.get(CONF_WARNING_TYPE, WARNING_TYPE_LANDSLIDE)
            
            # Store selection and proceed to location step
            self.context["warning_type"] = warning_type
            self.context["lang"] = user_input.get(CONF_LANG, DEFAULT_LANG)
            self.context["test_mode"] = user_input.get(CONF_TEST_MODE, False)
            self.context["enable_notifications"] = user_input.get(CONF_ENABLE_NOTIFICATIONS, False)
            self.context["notification_severity"] = user_input.get(CONF_NOTIFICATION_SEVERITY, NOTIFICATION_SEVERITY_YELLOW_PLUS)
            return await self.async_step_location()

        # Show warning type selection form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_WARNING_TYPE, default=WARNING_TYPE_LANDSLIDE): vol.In({
                    WARNING_TYPE_LANDSLIDE: "Landslide",
                    WARNING_TYPE_FLOOD: "Flood",
                    WARNING_TYPE_AVALANCHE: "Avalanche",
                    WARNING_TYPE_METALERTS: "Weather Alerts (Met.no)",
                }),
                vol.Optional(CONF_LANG, default=DEFAULT_LANG): vol.In(["no", "en"]),
                vol.Optional(CONF_TEST_MODE, default=False): cv.boolean,
                vol.Optional(CONF_ENABLE_NOTIFICATIONS, default=False): cv.boolean,
                vol.Optional(CONF_NOTIFICATION_SEVERITY, default=NOTIFICATION_SEVERITY_YELLOW_PLUS): vol.In(NOTIFICATION_SEVERITIES),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_location(self, user_input=None):
        """Handle location configuration based on selected warning type."""
        errors = {}
        warning_type = self.context.get("warning_type", WARNING_TYPE_LANDSLIDE)
        
        # Determine what location fields we need
        needs_county = warning_type in [WARNING_TYPE_LANDSLIDE, WARNING_TYPE_FLOOD, WARNING_TYPE_AVALANCHE]
        needs_latlon = warning_type == WARNING_TYPE_METALERTS

        if user_input is not None:
            try:
                # Combine all data
                final_data = {
                    CONF_WARNING_TYPE: warning_type,
                    CONF_LANG: self.context.get("lang", DEFAULT_LANG),
                    CONF_TEST_MODE: self.context.get("test_mode", False),
                    CONF_ENABLE_NOTIFICATIONS: self.context.get("enable_notifications", False),
                    CONF_NOTIFICATION_SEVERITY: self.context.get("notification_severity", NOTIFICATION_SEVERITY_YELLOW_PLUS),
                }
                
                # Add county data if needed
                if needs_county:
                    county_id = user_input.get(CONF_COUNTY_ID)
                    if not county_id:
                        errors["base"] = "missing_county"
                        raise ValueError("County required")
                    
                    county_name = COUNTIES.get(county_id, "Unknown")
                    final_data[CONF_COUNTY_ID] = county_id
                    final_data[CONF_COUNTY_NAME] = county_name
                    final_data[CONF_MUNICIPALITY_FILTER] = user_input.get(CONF_MUNICIPALITY_FILTER, "")
                    
                    # Validate API connection for county-based warnings
                    await validate_api_connection(
                        self.hass,
                        county_id,
                        warning_type,
                        final_data[CONF_LANG],
                    )
                
                # Add lat/lon data if needed
                if needs_latlon:
                    latitude = user_input.get(CONF_LATITUDE)
                    longitude = user_input.get(CONF_LONGITUDE)
                    if latitude is None or longitude is None:
                        errors["base"] = "missing_location"
                        raise ValueError("Latitude and longitude required")
                    
                    final_data[CONF_LATITUDE] = latitude
                    final_data[CONF_LONGITUDE] = longitude

                # Create unique ID
                if needs_county:
                    unique_id = f"{final_data[CONF_COUNTY_ID]}_{warning_type}"
                    title = f"{final_data[CONF_COUNTY_NAME]} {warning_type.replace('_', ' ').title()}"
                else:
                    unique_id = f"{latitude:.4f}_{longitude:.4f}_{warning_type}"
                    title = f"Weather Alerts ({latitude:.2f}, {longitude:.2f})"
                
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=title,
                    data=final_data,
                )
            except ValueError as err:
                _LOGGER.error("Validation failed: %s", err)
                if "base" not in errors:
                    errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Build conditional schema based on needs
        schema_dict = {}
        
        if needs_county:
            schema_dict[vol.Required(CONF_COUNTY_ID, default="46")] = vol.In(
                {k: v for k, v in sorted(COUNTIES.items(), key=lambda x: x[1])}
            )
            schema_dict[vol.Optional(CONF_MUNICIPALITY_FILTER, default="")] = cv.string
        
        if needs_latlon:
            # Default to Home Assistant's location
            default_lat = self.hass.config.latitude
            default_lon = self.hass.config.longitude
            schema_dict[vol.Required(CONF_LATITUDE, default=default_lat)] = cv.latitude
            schema_dict[vol.Required(CONF_LONGITUDE, default=default_lon)] = cv.longitude
        
        data_schema = vol.Schema(schema_dict)

        return self.async_show_form(
            step_id="location",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return VarsomOptionsFlow()


class VarsomOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Varsom Alerts."""

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            try:
                warning_type = user_input.get(CONF_WARNING_TYPE)
                needs_county = warning_type in [WARNING_TYPE_LANDSLIDE, WARNING_TYPE_FLOOD, WARNING_TYPE_AVALANCHE]
                needs_latlon = warning_type == WARNING_TYPE_METALERTS
                
                # Validate based on warning type
                if needs_county:
                    county_id = user_input.get(CONF_COUNTY_ID)
                    if not county_id:
                        errors["base"] = "missing_county"
                        raise ValueError("County required")
                    
                    # Validate the API connection with new settings
                    await validate_api_connection(
                        self.hass,
                        county_id,
                        warning_type,
                        user_input.get(CONF_LANG, DEFAULT_LANG),
                    )
                    
                    # Get county name from ID
                    county_name = COUNTIES.get(county_id, "Unknown")
                    user_input[CONF_COUNTY_NAME] = county_name
                
                if needs_latlon:
                    latitude = user_input.get(CONF_LATITUDE)
                    longitude = user_input.get(CONF_LONGITUDE)
                    if latitude is None or longitude is None:
                        errors["base"] = "missing_location"
                        raise ValueError("Latitude and longitude required")

                return self.async_create_entry(title="", data=user_input)
            except ValueError as err:
                _LOGGER.error("Validation failed: %s", err)
                if "base" not in errors:
                    errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Get current values from config entry (options take precedence over data)
        current_warning_type = self.config_entry.options.get(
            CONF_WARNING_TYPE, self.config_entry.data.get(CONF_WARNING_TYPE, DEFAULT_WARNING_TYPE)
        )
        current_lang = self.config_entry.options.get(
            CONF_LANG, self.config_entry.data.get(CONF_LANG, DEFAULT_LANG)
        )
        current_test_mode = self.config_entry.options.get(
            CONF_TEST_MODE, self.config_entry.data.get(CONF_TEST_MODE, False)
        )
        current_enable_notifications = self.config_entry.options.get(
            CONF_ENABLE_NOTIFICATIONS, self.config_entry.data.get(CONF_ENABLE_NOTIFICATIONS, False)
        )
        current_notification_severity = self.config_entry.options.get(
            CONF_NOTIFICATION_SEVERITY, self.config_entry.data.get(CONF_NOTIFICATION_SEVERITY, NOTIFICATION_SEVERITY_YELLOW_PLUS)
        )
        
        # Determine what location fields to show
        needs_county = current_warning_type in [WARNING_TYPE_LANDSLIDE, WARNING_TYPE_FLOOD, WARNING_TYPE_AVALANCHE]
        needs_latlon = current_warning_type == WARNING_TYPE_METALERTS
        
        # Build schema based on warning type
        schema_dict = {
            vol.Required(CONF_WARNING_TYPE, default=current_warning_type): vol.In({
                WARNING_TYPE_LANDSLIDE: "Landslide",
                WARNING_TYPE_FLOOD: "Flood",
                WARNING_TYPE_AVALANCHE: "Avalanche",
                WARNING_TYPE_METALERTS: "Weather Alerts (Met.no)",
            }),
        }
        
        if needs_county:
            current_county_id = self.config_entry.options.get(
                CONF_COUNTY_ID, self.config_entry.data.get(CONF_COUNTY_ID, "46")
            )
            current_municipality_filter = self.config_entry.options.get(
                CONF_MUNICIPALITY_FILTER, self.config_entry.data.get(CONF_MUNICIPALITY_FILTER, "")
            )
            schema_dict[vol.Required(CONF_COUNTY_ID, default=current_county_id)] = vol.In(
                {k: v for k, v in sorted(COUNTIES.items(), key=lambda x: x[1])}
            )
            schema_dict[vol.Optional(CONF_MUNICIPALITY_FILTER, default=current_municipality_filter)] = cv.string
        
        if needs_latlon:
            current_latitude = self.config_entry.options.get(
                CONF_LATITUDE, self.config_entry.data.get(CONF_LATITUDE, self.hass.config.latitude)
            )
            current_longitude = self.config_entry.options.get(
                CONF_LONGITUDE, self.config_entry.data.get(CONF_LONGITUDE, self.hass.config.longitude)
            )
            schema_dict[vol.Required(CONF_LATITUDE, default=current_latitude)] = cv.latitude
            schema_dict[vol.Required(CONF_LONGITUDE, default=current_longitude)] = cv.longitude
        
        schema_dict.update({
            vol.Optional(CONF_LANG, default=current_lang): vol.In(["no", "en"]),
            vol.Optional(CONF_TEST_MODE, default=current_test_mode): cv.boolean,
            vol.Optional(CONF_ENABLE_NOTIFICATIONS, default=current_enable_notifications): cv.boolean,
            vol.Optional(CONF_NOTIFICATION_SEVERITY, default=current_notification_severity): vol.In(NOTIFICATION_SEVERITIES),
        })
        
        data_schema = vol.Schema(schema_dict)

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )
