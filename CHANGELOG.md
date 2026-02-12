# Changelog

All notable changes to the Norway Alerts integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.4.0] - 2026-02-12

### Added
- **Split Ongoing and Expected Alerts** - Separate formatted content attributes for better display control
  - New `formatted_content_expected` attribute for alerts that haven't started yet
  - Existing `formatted_content` now only shows ongoing alerts (already started)
  - New `ongoing_alerts` count attribute (number of alerts already active)
  - New `expected_alerts` count attribute (number of alerts starting in the future)
  - State (`active_alerts`) remains the total count of all alerts
  - Enables separate display cards for current vs. upcoming alerts
  - Alert timing based on `starttime` field compared to current time
  - Both attributes available for CAP-formatted sensors only

### Technical Details
- Alerts are split based on their `starttime` field
- If `starttime > now`: classified as "expected" (future)
- If `starttime <= now` or no starttime: classified as "ongoing" (current)
- `formatted_summary` continues to show all alerts (combined) as before
- Timezone-aware comparison handles both naive and aware datetimes

## [2.3.2]

### Changed
- **🎨 Enhanced Visual Layout** - Improved alert display with Home Assistant markdown card
  - Banner-style `<ha-alert>` boxes for visual hierarchy
  - Alert icons displayed in separate colored alert header (color based on severity)
  - Severity-based coloring: Red (Severe/Extreme), Orange (Moderate/Minor), Blue (Unknown)
  - Each alert shown in colored box with event name and status as title
  - Time periods displayed in styled table (bold labels, italic values) within alert
  - All alert details (description, instructions, consequences, area) contained within alert box
  - Better visual alignment and background for comprehensive alert information
  - Removed markdown headers (####) in favor of bold text within alerts

## [2.3.1]

### Changed
- **Event Name Translations** - Refined translations to match official Met.no CAP documentation
  - English: "Forest fire" → "Forest fire danger", "Wind" → "Vindkast"
  - Norwegian: "Skogbrann" → "Skogbrannfare", "Lyn" → "Mye lyn", "Polarlågtrykksvarsling" → "Polart lavtrykk"
  - Maintained readable translations for stormSurge: "Storm surge" / "Stormflo"
- **💾 Recorder Optimization** - Excluded large attributes from state history
  - `alerts`, `formatted_content`, `formatted_summary`, and `entity_picture` excluded from recorder
  - Significantly reduces database size without losing functionality
  - State and `active_alerts` still recorded for history graphs
  - Follows Home Assistant best practices for attributes not suitable for history

## [2.3.0]

- **Norwegian Language Support** - Full Norwegian translations
  - Norwegian template (formatted_content_no.j2) with translated headings
  - Norwegian translations for config flow UI (no.json)
  - Automatic language detection based on sensor configuration
  - Norwegian date/time formatting (e.g., "Torsdag, 05. februar kl. 23:00")
  - Event name translations using official Met.no CAP v.1 Profile documentation
  - Examples: "blowingSnow" → "Snøfokk" / "Blowing snow", "forestFire" → "Skogbrannfare" / "Forest fire danger"

## [2.2.0] - 2026-01-23

### Added
- **Formatted Content Attribute** - Automatic markdown formatting for CAP-formatted alerts
  - Available for CAP sensors: Weather alerts (always) and NVE warnings with CAP enabled
  - Generated using Jinja2 template engine
  - Ready-to-use display format for markdown cards without custom templates
  - Configurable display options: show_icon, show_status, show_map
  - Includes alert status (Expected/Ongoing/Ended), severity, descriptions, instructions, consequences
  - No template logic required in dashboard cards
- **Compact View Toggle** - Switch entity for toggling between compact and full view
  - Compact view: All alert icons in a single row
  - Full view: Detailed information for each alert
  - Automatic detection and re-linking on entity rename


### Changed
- **CAP Format Option** - Hidden for weather alerts in config flow
  - Only shown for NVE warnings (landslide, flood, avalanche)
  - MetAlerts are always in CAP format (option not applicable)

## [2.1.0] - 2026-01-13

### Breaking Changes
- **Sensor state changed**: State now represents the count of active alerts
  - Previous: State was highest activity level (1-5) or text string "1" for no alerts
  - Current: State is integer count (0 = no alerts, 1 = one alert, 2 = two alerts, etc.)
  - Severity information still available in `highest_level` and `highest_level_numeric` attributes
  - **Impact**: Automations or templates using `states('sensor.norway_alerts_*')` for severity level need updating

### Added
- **CAP format conversion** - Optional conversion of NVE warnings to CAP (Common Alerting Protocol) format
  - Enabled by default for new sensors
  - Existing sensors preserve their original format for backward compatibility
  - Allows unified display of NVE and Met.no alerts using the same template
  - Only available for NVE warnings (landslide, flood, avalanche) - Met.no alerts are always CAP
- **Template blueprint** - Pre-built template sensor blueprint for displaying CAP-formatted alerts
  - Available in `blueprints/template/cap_alert_markdown_sensor.yaml`
  - Import from GitHub for easy setup
  - Configurable display options (icons, status, maps)
  - Creates formatted markdown sensor for use in markdown cards

### Changed
- CAP format option hidden for Met.no weather alerts (always CAP format)

## [2.0.0] - 2026-01-09

### Breaking Changes
- **Integration renamed**: `varsom` → `norway_alerts`
  - Domain changed to better reflect all warning types (geohazards + weather)
  - Custom component directory: `/custom_components/norway_alerts/`
  - Sensors now prefixed with `sensor.norway_alerts_*`
  - Requires removal of old integration and re-adding with new name

### Added
- **Met.no MetAlerts API integration** - Weather warnings from Norwegian Meteorological Institute
  - Support for all meteorological warning types (wind, rain, snow, thunderstorms, etc.)
  - Latitude/longitude-based location configuration
  - CAP (Common Alerting Protocol) format support
- **Avalanche warnings** - Full support for NVE avalanche warnings
  - 5-level severity scale (green, yellow, orange, red, black)
  - Avalanche-specific attributes and data
- **Two-step configuration flow** - Improved setup process
  - Step 1: Select warning type and general settings
  - Step 2: Conditional location fields (county OR coordinates)
- **Persistent notifications** - Optional notification system
  - Configurable severity thresholds
  - Notifications for new or changed alerts
  - Severity filter options (all, yellow+, orange+, red only)
- **Test mode** - Generate fake alerts for testing dashboards and automations

### Changed
- **Architecture**: One sensor per warning type (cleaner separation)
  - Each configuration creates a single dedicated sensor
  - Users add integration multiple times for different types
  - Better attribute organization per warning type
- **Location handling**: Conditional fields based on warning type
  - NVE warnings (landslide/flood/avalanche): County-based with municipality filter
  - Met.no weather alerts: Latitude/longitude coordinates
  - Default coordinates from Home Assistant location (editable)
- **API Factory pattern**: Unified API client architecture
  - BaseWarningAPI abstract class
  - Separate API classes for each warning source
  - Consistent data format across all warning types

### Technical Details
- Based on MIT-licensed code from @kutern84 and @svenove (met_alerts)
- Proper attribution maintained in source code
- Updated WarningAPIFactory to support latitude/longitude parameters
- Enhanced error handling for different location types
- Backward compatibility for existing configurations

### Documentation
- **Consolidated README.md** - All documentation in one place
  - MetAlerts configuration and usage
  - Avalanche warnings documentation
  - Updated examples for all warning types
  - Architecture explanation
- **Removed obsolete files**:
  - NOTIFICATION_EXAMPLES.md
  - REFACTORING_SUMMARY.md
  - FRONTEND_EXAMPLES.md
  - DEV_SUMMARY.md
  - COMPLETE_DASHBOARD_EXAMPLE.md
  - AVALANCHE_FILTERING_GUIDE.md
  - AVALANCHE_DISPLAY_EXAMPLES.md
  - AVALANCHE_ATTRIBUTES_UPDATE.md
  - notes/ directory

### Credits
- Met.no MetAlerts integration code: @kutern84 and @svenove
- Original met_alerts repository: https://github.com/kurtern84/met_alerts

## [1.0.0] - 2025-12-15

### Added
- Initial release of Varsom Alerts integration
- Single sensor per county with all alerts in attributes
- Support for landslide warnings from NVE API
- Support for flood warnings from NVE API
- Option to monitor both warning types simultaneously
- County selection from all Norwegian counties
- Bilingual support (Norwegian and English)
- Config flow for easy setup through UI
- Rich alert data including:
  - Activity levels (1-4: green, yellow, orange, red)
  - Danger types and warning text
  - Affected municipalities
  - Valid from/to timestamps
  - Advice and consequence information
  - Direct links to Varsom.no with interactive maps
- Automatic icon updates based on alert level
- 30-minute update interval for fresh data

### Technical Details
- Uses DataUpdateCoordinator pattern for efficient API polling
- Implements modern Home Assistant best practices
- Single sensor design (not multiple _2, _3, _4 sensors like older integrations)
- All alerts accessible via structured attributes array
- Proper error handling and logging

### Documentation
- Comprehensive README with usage examples
- Template sensor examples for municipality filtering
- Automation examples for notifications
- Lovelace card configuration examples

[1.0.0]: https://github.com/DTekNO/varsom/releases/tag/v1.0.0
