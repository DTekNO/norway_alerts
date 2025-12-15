"""Constants for the Varsom Alerts integration."""

DOMAIN = "varsom"
DEFAULT_NAME = "Varsom Alerts"
DEFAULT_LANG = "en"
DEFAULT_WARNING_TYPE = "landslide"
CONF_LANG = "lang"
CONF_COUNTY_ID = "county_id"
CONF_COUNTY_NAME = "county_name"
CONF_WARNING_TYPE = "warning_type"
CONF_MUNICIPALITY_FILTER = "municipality_filter"
CONF_USE_LOCATION = "use_location"
PLATFORMS = ["sensor"]

# NVE API Base URLs
API_BASE_LANDSLIDE = "https://api01.nve.no/hydrology/forecast/landslide/v1.0.10/api"
API_BASE_FLOOD = "https://api01.nve.no/hydrology/forecast/flood/v1.0.10/api"

# Warning types
WARNING_TYPE_LANDSLIDE = "landslide"
WARNING_TYPE_FLOOD = "flood"
WARNING_TYPE_BOTH = "both"

# Activity levels
ACTIVITY_LEVEL_GREEN = "1"
ACTIVITY_LEVEL_YELLOW = "2"
ACTIVITY_LEVEL_ORANGE = "3"
ACTIVITY_LEVEL_RED = "4"

ACTIVITY_LEVEL_NAMES = {
    "1": "green",
    "2": "yellow",
    "3": "orange",
    "4": "red",
}

# Norwegian counties with IDs (based on NVE API)
COUNTIES = {
    "03": "Oslo",
    "11": "Rogaland",
    "15": "Møre og Romsdal",
    "18": "Nordland",
    "30": "Viken",
    "34": "Innlandet",
    "38": "Vestfold og Telemark",
    "42": "Agder",
    "46": "Vestland",
    "50": "Trøndelag",
    "54": "Troms og Finnmark",
}
