"""Config flow for Varsom Alerts integration."""
import asyncio
import logging

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
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
    WARNING_TYPE_BOTH,
    WARNING_TYPE_ALL,
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
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Validate the API connection
                await validate_api_connection(
                    self.hass,
                    user_input[CONF_COUNTY_ID],
                    user_input[CONF_WARNING_TYPE],
                    user_input.get(CONF_LANG, DEFAULT_LANG),
                )

                # Get county name from ID
                county_name = COUNTIES.get(user_input[CONF_COUNTY_ID], "Unknown")
                user_input[CONF_COUNTY_NAME] = county_name

                # Create a unique ID based on county and warning type
                await self.async_set_unique_id(
                    f"{user_input[CONF_COUNTY_ID]}_{user_input[CONF_WARNING_TYPE]}"
                )
                self._abort_if_unique_id_configured()

                # Use county name and warning type in title
                warning_type_str = user_input[CONF_WARNING_TYPE].replace("_", " ").title()
                title = f"{county_name} {warning_type_str}"

                return self.async_create_entry(
                    title=title,
                    data=user_input,
                )
            except ValueError as err:
                _LOGGER.error("Validation failed: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Show the form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_COUNTY_ID, default="46"): vol.In(
                    {k: v for k, v in sorted(COUNTIES.items(), key=lambda x: x[1])}
                ),
                vol.Required(CONF_WARNING_TYPE, default=DEFAULT_WARNING_TYPE): vol.In({
                    WARNING_TYPE_LANDSLIDE: "Landslide",
                    WARNING_TYPE_FLOOD: "Flood",
                    WARNING_TYPE_AVALANCHE: "Avalanche",
                    WARNING_TYPE_BOTH: "Landslide & Flood",
                    WARNING_TYPE_ALL: "All (Landslide, Flood & Avalanche)",
                }),
                vol.Optional(CONF_LANG, default=DEFAULT_LANG): vol.In(["no", "en"]),
                vol.Optional(CONF_MUNICIPALITY_FILTER, default=""): cv.string,
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
                # Validate the API connection with new settings
                await validate_api_connection(
                    self.hass,
                    user_input[CONF_COUNTY_ID],
                    user_input[CONF_WARNING_TYPE],
                    user_input.get(CONF_LANG, DEFAULT_LANG),
                )

                # Get county name from ID
                county_name = COUNTIES.get(user_input[CONF_COUNTY_ID], "Unknown")
                user_input[CONF_COUNTY_NAME] = county_name

                return self.async_create_entry(title="", data=user_input)
            except ValueError as err:
                _LOGGER.error("Validation failed: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Get current values from config entry (options take precedence over data)
        current_county_id = self.config_entry.options.get(
            CONF_COUNTY_ID, self.config_entry.data.get(CONF_COUNTY_ID, "46")
        )
        current_warning_type = self.config_entry.options.get(
            CONF_WARNING_TYPE, self.config_entry.data.get(CONF_WARNING_TYPE, DEFAULT_WARNING_TYPE)
        )
        current_lang = self.config_entry.options.get(
            CONF_LANG, self.config_entry.data.get(CONF_LANG, DEFAULT_LANG)
        )
        current_municipality_filter = self.config_entry.options.get(
            CONF_MUNICIPALITY_FILTER, self.config_entry.data.get(CONF_MUNICIPALITY_FILTER, "")
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

        data_schema = vol.Schema(
            {
                vol.Required(CONF_COUNTY_ID, default=current_county_id): vol.In(
                    {k: v for k, v in sorted(COUNTIES.items(), key=lambda x: x[1])}
                ),
                vol.Required(CONF_WARNING_TYPE, default=current_warning_type): vol.In({
                    WARNING_TYPE_LANDSLIDE: "Landslide",
                    WARNING_TYPE_FLOOD: "Flood",
                    WARNING_TYPE_BOTH: "Landslide & Flood",
                    WARNING_TYPE_AVALANCHE: "Avalanche",
                    WARNING_TYPE_ALL: "All (Landslide, Flood & Avalanche)",
                }),
                vol.Optional(CONF_LANG, default=current_lang): vol.In(["no", "en"]),
                vol.Optional(CONF_MUNICIPALITY_FILTER, default=current_municipality_filter): cv.string,
                vol.Optional(CONF_TEST_MODE, default=current_test_mode): cv.boolean,
                vol.Optional(CONF_ENABLE_NOTIFICATIONS, default=current_enable_notifications): cv.boolean,
                vol.Optional(CONF_NOTIFICATION_SEVERITY, default=current_notification_severity): vol.In(NOTIFICATION_SEVERITIES),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )
