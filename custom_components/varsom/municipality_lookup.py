"""Municipality lookup helper for Varsom integration."""
import logging

_LOGGER = logging.getLogger(__name__)

# Basic municipality lookup by approximate coordinates
# This is a simple implementation - can be enhanced with GeoJSON boundaries
MUNICIPALITY_LOOKUP = {
    # Vestland county municipalities (approximate center points)
    "Alver": {"lat_range": (60.5, 60.8), "lon_range": (5.0, 5.4), "county": "46"},
    "Askvoll": {"lat_range": (61.2, 61.5), "lon_range": (5.0, 5.4), "county": "46"},
    "Askøy": {"lat_range": (60.4, 60.5), "lon_range": (5.0, 5.2), "county": "46"},
    "Aurland": {"lat_range": (60.8, 61.1), "lon_range": (6.8, 7.4), "county": "46"},
    "Bergen": {"lat_range": (60.3, 60.5), "lon_range": (5.1, 5.5), "county": "46"},
    "Bjørnafjorden": {"lat_range": (60.0, 60.3), "lon_range": (5.4, 5.8), "county": "46"},
    "Bømlo": {"lat_range": (59.6, 59.9), "lon_range": (5.1, 5.4), "county": "46"},
    "Etne": {"lat_range": (59.6, 59.9), "lon_range": (5.8, 6.2), "county": "46"},
    "Fitjar": {"lat_range": (59.8, 60.0), "lon_range": (5.2, 5.4), "county": "46"},
    "Fjaler": {"lat_range": (61.2, 61.5), "lon_range": (5.4, 5.8), "county": "46"},
    "Gloppen": {"lat_range": (61.6, 61.9), "lon_range": (6.4, 6.8), "county": "46"},
    "Gulen": {"lat_range": (60.9, 61.2), "lon_range": (5.0, 5.4), "county": "46"},
    "Hyllestad": {"lat_range": (61.1, 61.3), "lon_range": (5.2, 5.5), "county": "46"},
    "Høyanger": {"lat_range": (61.1, 61.3), "lon_range": (5.9, 6.4), "county": "46"},
    "Kinn": {"lat_range": (61.4, 61.9), "lon_range": (4.9, 5.4), "county": "46"},
    "Kvam": {"lat_range": (60.3, 60.6), "lon_range": (5.9, 6.4), "county": "46"},
    "Kvinnherad": {"lat_range": (59.8, 60.2), "lon_range": (5.8, 6.3), "county": "46"},
    "Luster": {"lat_range": (61.3, 61.8), "lon_range": (7.1, 7.9), "county": "46"},
    "Lærdal": {"lat_range": (61.0, 61.2), "lon_range": (7.3, 7.7), "county": "46"},
    "Masfjorden": {"lat_range": (60.7, 60.9), "lon_range": (5.3, 5.7), "county": "46"},
    "Modalen": {"lat_range": (60.7, 60.9), "lon_range": (5.7, 6.0), "county": "46"},
    "Osterøy": {"lat_range": (60.5, 60.7), "lon_range": (5.4, 5.7), "county": "46"},
    "Samnanger": {"lat_range": (60.4, 60.6), "lon_range": (5.6, 5.8), "county": "46"},
    "Sogndal": {"lat_range": (61.1, 61.3), "lon_range": (6.9, 7.2), "county": "46"},
    "Solund": {"lat_range": (61.0, 61.2), "lon_range": (4.7, 5.0), "county": "46"},
    "Stad": {"lat_range": (62.0, 62.4), "lon_range": (5.4, 5.9), "county": "46"},
    "Stord": {"lat_range": (59.7, 59.9), "lon_range": (5.4, 5.6), "county": "46"},
    "Stryn": {"lat_range": (61.8, 62.1), "lon_range": (6.6, 7.3), "county": "46"},
    "Sunnfjord": {"lat_range": (61.4, 61.7), "lon_range": (5.8, 6.3), "county": "46"},
    "Sveio": {"lat_range": (59.5, 59.7), "lon_range": (5.3, 5.5), "county": "46"},
    "Tysnes": {"lat_range": (59.9, 60.1), "lon_range": (5.4, 5.7), "county": "46"},
    "Ullensvang": {"lat_range": (60.2, 60.6), "lon_range": (6.4, 7.0), "county": "46"},
    "Ulvik": {"lat_range": (60.5, 60.7), "lon_range": (6.8, 7.1), "county": "46"},
    "Vaksdal": {"lat_range": (60.5, 60.7), "lon_range": (5.7, 6.2), "county": "46"},
    "Vestland fylkeskommune": {"lat_range": (60.3, 60.5), "lon_range": (5.2, 5.4), "county": "46"},
    "Vik": {"lat_range": (61.0, 61.2), "lon_range": (6.3, 6.7), "county": "46"},
    "Voss": {"lat_range": (60.5, 60.8), "lon_range": (6.3, 6.8), "county": "46"},
    "Øygarden": {"lat_range": (60.4, 60.6), "lon_range": (4.8, 5.1), "county": "46"},
    "Årdal": {"lat_range": (61.1, 61.4), "lon_range": (7.5, 7.9), "county": "46"},
}


def get_municipality_from_coordinates(latitude: float, longitude: float) -> tuple[str, str] | None:
    """
    Get municipality name and county ID from lat/lon coordinates.
    
    Returns tuple of (municipality_name, county_id) or None if not found.
    
    This is a basic implementation using bounding boxes.
    For more accuracy, use GeoJSON polygon intersection.
    """
    _LOGGER.debug("Looking up municipality for coordinates: %s, %s", latitude, longitude)
    
    matches = []
    for municipality, data in MUNICIPALITY_LOOKUP.items():
        lat_min, lat_max = data["lat_range"]
        lon_min, lon_max = data["lon_range"]
        
        if lat_min <= latitude <= lat_max and lon_min <= longitude <= lon_max:
            matches.append((municipality, data["county"]))
            _LOGGER.debug("Found match: %s (county %s)", municipality, data["county"])
    
    if not matches:
        _LOGGER.warning("No municipality found for coordinates: %s, %s", latitude, longitude)
        return None
    
    if len(matches) > 1:
        _LOGGER.warning("Multiple municipalities found for coordinates: %s, %s - using first match", latitude, longitude)
    
    return matches[0]


def load_geojson_boundaries(geojson_path: str) -> dict:
    """
    Load municipality boundaries from GeoJSON file.
    
    This function can be implemented to use precise polygon boundaries
    instead of the approximate bounding boxes above.
    
    Parameters:
        geojson_path: Path to GeoJSON file with municipality boundaries
    
    Returns:
        Dictionary mapping municipality names to boundary polygons
    """
    # TODO: Implement GeoJSON loading
    # Can use shapely library for point-in-polygon tests
    raise NotImplementedError("GeoJSON boundary loading not yet implemented")


def get_municipality_from_coordinates_precise(
    latitude: float, 
    longitude: float, 
    boundaries: dict
) -> tuple[str, str] | None:
    """
    Get municipality using precise GeoJSON polygon boundaries.
    
    Parameters:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        boundaries: Municipality boundaries from load_geojson_boundaries()
    
    Returns:
        tuple of (municipality_name, county_id) or None if not found
    """
    # TODO: Implement point-in-polygon check using shapely
    # from shapely.geometry import Point, shape
    # point = Point(longitude, latitude)
    # for municipality, geojson_feature in boundaries.items():
    #     polygon = shape(geojson_feature['geometry'])
    #     if polygon.contains(point):
    #         return (municipality, geojson_feature['properties']['county_id'])
    raise NotImplementedError("Precise GeoJSON lookup not yet implemented")
