# GitHub Copilot Instructions - Norway Alerts Integration

## Project Overview

**Norway Alerts** is a Home Assistant custom integration that provides weather warnings (Met.no MetAlerts) and geohazard warnings (NVE: landslide, flood, avalanche) for locations in Norway.

### Key Technologies
- **Platform**: Home Assistant custom component
- **Language**: Python 3.11+
- **APIs**: Met.no MetAlerts (CAP XML), NVE JSON APIs
- **Format Standards**: CAP (Common Alerting Protocol) v1.2/v2.0

## Architecture

### Data Sources
1. **Met.no MetAlerts** (coordinate-based)
   - Weather warnings: wind, rain, snow, lightning, forestFire, etc.
   - Native CAP XML format (already standardized)
   - URL: `https://api.met.no/weatherapi/metalerts/2.0`

2. **NVE Warnings** (county-based)
   - Landslide/flood: Custom JSON format
   - Avalanche: Custom JSON format  
   - URLs: `api01.nve.no/hydrology/forecast/{type}/v1.0.10/api`

### Key Components

#### API Layer (`api.py`)
- `BaseWarningAPI`: Abstract base class for all warning sources
- `CountyBasedAPI`: Base for NVE county-based APIs
- `LandslideAPI`, `FloodAPI`, `AvalancheAPI`: NVE implementations
- `MetAlertsAPI`: Met.no CAP XML implementation
- `WarningAPIFactory`: Factory pattern for API instantiation

#### Data Coordinator (`sensor.py`)
- `WarningDataUpdateCoordinator`: Manages data fetching and updates
- `WarningTypeSensor`: Main sensor entity implementation
- `convert_nve_to_cap()`: Converts NVE JSON to CAP-like structure

#### Configuration (`config_flow.py`)
- Two-step configuration flow
- Step 1: Warning type and general settings
- Step 2: Location (county OR coordinates)

## Critical Concepts

### CAP Format Support
The integration supports an optional **CAP conversion mode** for NVE warnings:
- Enabled via `cap_format` configuration option (default: True)
- When enabled, NVE JSON is converted to CAP-like structure using `convert_nve_to_cap()`
- Allows unified display templates for both NVE and Met.no alerts
- Met.no alerts are always CAP (option hidden in config flow)

### Future NVE CAP Migration 🔮
**IMPORTANT**: NVE is expected to adopt native CAP XML format in the future, following the Met.no/MetCoOp CAP v.2 Profile specification (https://docs.api.met.no/doc/metalerts/CAP-v2-profile.html).

**When this happens:**
1. The current `convert_nve_to_cap()` function will become obsolete
2. NVE APIs (`LandslideAPI`, `FloodAPI`, `AvalancheAPI`) will need to parse CAP XML instead of JSON
3. Detection logic should be added to check response format (XML vs JSON)
4. The `cap_format` option may become redundant (all sources will be native CAP)
5. Event codes will need expansion to include NVE-specific types

**Current architecture is future-ready** - minimal changes required when NVE switches to CAP.

### Icon System
- Icons stored as base64-encoded SVGs in `const.py` (`ICON_DATA_URLS`)
- Naming: `{type}-{color}` (e.g., `rain-orange`, `forestfire-red`)
- Composite icons: Multiple alerts rendered as horizontally stacked SVG (512px base, 128px offset)
- High resolution: Scaled from 48px to 512px for `entity_picture`

### Bilingual Support
- Languages: Norwegian (`no`) and English (`en`)
- Event name translations via `_translate_event_name()` method
- Translations follow official Met.no CAP v.1 Profile documentation
- Templates: `formatted_content.j2` (English), `formatted_content_no.j2` (Norwegian)

## Coding Standards

### Naming Conventions
- Classes: `PascalCase` (e.g., `WarningDataUpdateCoordinator`)
- Functions/methods: `snake_case` (e.g., `fetch_warnings`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `API_BASE_METALERTS`)
- Private methods: `_leading_underscore` (e.g., `_translate_event_name`)

### Logging
- Use module-level logger: `_LOGGER = logging.getLogger(__name__)`
- Levels:
  - `DEBUG`: API requests, raw data inspection
  - `INFO`: Successful operations, data counts
  - `WARNING`: Recoverable issues, fallback behavior
  - `ERROR`: API failures, unexpected data format

### Error Handling
- Always wrap API calls in `try/except` with timeout
- Return empty list `[]` on API failure (graceful degradation)
- Log errors with context (warning type, county, coordinates)
- Use `asyncio.timeout(10)` for all network requests

### User-Agent
- Always include User-Agent header in API requests
- Format: `norway_alerts/{version} jeremy.m.cook@gmail.com`
- Version read from `manifest.json` at module import time

## Common Patterns

### Fetching Warnings
```python
async with aiohttp.ClientSession() as session:
    async with asyncio.timeout(10):
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                _LOGGER.error("Error fetching data: %s", response.status)
                return []
            data = await response.json()
            return data
```

### CAP Field Mapping
When working with CAP data or converting to CAP:
- `event`: Human-readable event name (e.g., "Forest fire danger")
- `eventType`: Coded type (e.g., "forestFire")
- `severity`: OASIS values ("Minor", "Moderate", "Severe", "Extreme")
- `certainty`: OASIS values ("Possible", "Likely", "Observed")
- `awareness_level`: Format `"{level}; {color}; {name}"` (e.g., "3; orange; Severe")

### Activity Level to Color Mapping
```python
ACTIVITY_LEVEL_NAMES = {
    "0": "white",    # No data
    "1": "green",    # Low risk
    "2": "yellow",   # Moderate risk
    "3": "orange",   # Considerable risk
    "4": "red",      # High risk
    "5": "black",    # Extreme risk (avalanche only)
}
```

## Testing

### Manual Testing Scripts
- `tests/manual_nve_api.py`: Test NVE API connectivity
- `tests/manual_metalerts_api.py`: Test Met.no MetAlerts API
- Run with: `python -m tests.manual_nve_api`

### Unit Tests
- Located in `tests/` directory
- Use pytest: `pytest tests/`
- Mock API responses for deterministic testing

## Template System

### Jinja2 Templates
- Location: `custom_components/norway_alerts/templates/`
- `formatted_content.j2`: English markdown template
- `formatted_content_no.j2`: Norwegian markdown template
- Variables passed: `alerts`, `compact_view`, `show_icon`, `show_status`, `show_map`

### Template Rendering
```python
template = env.get_template("formatted_content.j2")
rendered = template.render(
    alerts=enriched_alerts,
    compact_view=compact_view,
    show_icon=True,
    show_status=True,
    show_map=False,
    now_timestamp=time.time()
)
```

## Configuration Options

### Core Settings
- `warning_type`: "weather", "landslide", "flood", "avalanche"
- `county_id`: Norwegian county code (NVE warnings only)
- `latitude`/`longitude`: Coordinates (Met.no alerts only)
- `language`: "en" or "no"
- `cap_format`: Convert NVE to CAP (default: True)

### Optional Settings
- `municipality_filter`: Filter by municipality name (NVE only)
- `enable_notifications`: Persistent notifications for new/changed alerts
- `notification_severity`: Filter threshold ("all", "yellow", "orange", "red")
- `test_mode`: Generate fake alerts for testing

## File Structure

```
custom_components/norway_alerts/
├── __init__.py              # Integration setup, coordinator initialization
├── sensor.py                # Main sensor, CAP conversion, template rendering
├── api.py                   # API clients for all warning sources
├── config_flow.py           # Two-step configuration UI
├── const.py                 # Constants, icons, county mappings
├── strings.json             # English UI translations
├── translations/
│   └── no.json             # Norwegian UI translations
├── templates/
│   ├── formatted_content.j2    # English alert template
│   └── formatted_content_no.j2 # Norwegian alert template
└── manifest.json           # Integration metadata
```

## References

- [Met.no CAP v.1 Profile](https://docs.api.met.no/doc/metalerts/CAP-v1-profile.html)
- [Met.no CAP v.2 Profile (Draft)](https://docs.api.met.no/doc/metalerts/CAP-v2-profile.html) - Future NVE format
- [OASIS CAP 1.2 Standard](http://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html)
- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Varsom.no](https://www.varsom.no/) - NVE warning portal

## Contributing Notes

When adding new features:
1. Update `CHANGELOG.md` with version and changes
2. Update `README.md` examples if user-facing
3. Maintain bilingual support (Norwegian/English)
4. Add tests for new API methods
5. Keep CAP conversion compatibility in mind for future NVE migration
6. Follow Home Assistant integration quality checklist
