# Norway Alerts - Switch Removal and Icon Updates

## Changes Made (February 9, 2026)

### Summary
Removed the binary switch entity for compact view toggling and replaced it with two separate sensor attributes: `formatted_content` (full details) and `formatted_summary` (compact icons). Also added default icon and state coloring to sensors.

---

## 1. Removed Switch Platform

**File: `const.py`**
- Changed `PLATFORMS = ["sensor", "switch"]` to `PLATFORMS = ["sensor"]`
- The switch.py file still exists but is no longer loaded by the integration

---

## 2. Sensor Updates

**File: `sensor.py`**

### Removed Code:
- ❌ `self._compact_view_switch_entity_id` attribute
- ❌ `async_added_to_hass()` method (switch listener setup)
- ❌ `_setup_switch_listener()` method
- ❌ All switch state checking logic in `_generate_formatted_content()`

### Added/Modified:

#### New Method Signature:
```python
def _generate_formatted_content(self, alerts, compact=False):
    """Generate markdown-formatted content for display.
    
    Args:
        alerts: List of alerts to format
        compact: If True, generate compact view (icons only), otherwise full details
    """
```

#### New Sensor Attributes:
```python
result = {
    "active_alerts": len(alerts_list),
    "highest_level": ACTIVITY_LEVEL_NAMES.get(str(max_level), "green"),
    "highest_level_numeric": max_level,
    "alerts": alerts_list,
    "formatted_content": self._generate_formatted_content(alerts_list, compact=False),  # Full details
    "formatted_summary": self._generate_formatted_content(alerts_list, compact=True),    # Compact icons
}
```

#### New Icon Properties:
```python
@property
def icon(self):
    """Return the icon for the sensor."""
    return "mdi:alert"

@property
def icon_color(self):
    """Return the color based on highest alert level."""
    # Returns: "yellow", "orange", or "red" based on alert level
    # Returns: None when no alerts
```

**State Color Mapping:**
- Level 2 (Yellow/Moderate) → `"yellow"`
- Level 3 (Orange/Severe) → `"orange"`
- Level 4 (Red/Extreme) → `"red"`
- Level 5 (Purple/Extreme) → `"red"`

---

## 3. Template Updates

**Files: `formatted_content.j2` and `formatted_content_no.j2`**

### Removed:
```jinja
{%- set switch_id = switch_entity_id if switch_entity_id else ('switch.' ~ entity_id.split('.')[1] ~ '_compact_view') -%}
{%- set switch_state_obj = states(switch_id) -%}
{%- set switch_state_value = switch_state_obj.state if switch_state_obj else 'unknown' -%}
{%- set compact_view = switch_state_value == 'on' -%}
<!-- DEBUG: entity_id={{ entity_id }}, switch={{ switch_id }}, state={{ switch_state_value }}, compact={{ compact_view }} -->
```

### Simplified:
Templates now receive `compact_view` as a direct parameter (True/False) instead of checking switch state.

---

## 4. Usage in Lovelace Cards

### Full Alert Details:
```yaml
type: markdown
content: |
  {{ state_attr('sensor.norway_alerts_metalerts_weather', 'formatted_content') }}
```

### Compact Icon View:
```yaml
type: markdown
content: |
  {{ state_attr('sensor.norway_alerts_metalerts_weather', 'formatted_summary') }}
```

### Custom Toggle (Optional):
If you still want a toggle button, use an `input_boolean` helper and conditional cards:

```yaml
# Create input_boolean.norway_alerts_compact_view in UI

# Card configuration:
type: conditional
conditions:
  - entity: input_boolean.norway_alerts_compact_view
    state: 'on'
card:
  type: markdown
  content: |
    {{ state_attr('sensor.norway_alerts_metalerts_weather', 'formatted_summary') }}
```

---

## 5. Benefits

✅ **Simpler architecture** - No switch entity to manage or link
✅ **No confusion** - Users just choose which attribute to display
✅ **Better icon** - `mdi:alert` instead of generic entity picture
✅ **State coloring** - Sensor icon color changes based on alert severity
✅ **More flexible** - Easy to use either view in any card without switches

---

## 6. Migration Guide

### For Existing Users:

1. **Remove old switch entities** (they'll appear unavailable):
   - Go to Settings → Devices & Services → Norway Alerts
   - Click on the device
   - Remove any "Compact View" switch entities

2. **Update Lovelace cards**:
   - Replace any conditional cards based on switch state
   - Use `formatted_content` or `formatted_summary` attributes directly

3. **Reload the integration**:
   - Settings → Devices & Services → Norway Alerts
   - Three dots menu → Reload

---

## 7. Technical Notes

### Entity Picture vs Icon:
- `entity_picture` - Still used for individual alert icons in formatted content (Yr.no warning icons)
- `icon` - New default sensor icon (`mdi:alert`) shown in entity cards
- `icon_color` - Dynamic state color based on highest alert level

### Template Rendering:
Both templates now accept a `compact_view` boolean parameter:
- When `compact=True` → Renders compact view (icons only)
- When `compact=False` → Renders full view (all details)

This is cleaner than checking switch state during rendering.

---

## Files Modified

1. ✅ `custom_components/norway_alerts/const.py` - Removed "switch" from PLATFORMS
2. ✅ `custom_components/norway_alerts/sensor.py` - Removed switch code, added icon properties, dual attributes
3. ✅ `custom_components/norway_alerts/templates/formatted_content.j2` - Simplified template
4. ✅ `custom_components/norway_alerts/templates/formatted_content_no.j2` - Simplified template

## Files NOT Modified (but affected)

- `custom_components/norway_alerts/switch.py` - Still exists but no longer loaded
- `custom_components/norway_alerts/__init__.py` - No changes needed (PLATFORMS imported from const.py)

---

## Testing Checklist

- [ ] Reload integration (no errors in logs)
- [ ] Verify sensors show `mdi:alert` icon
- [ ] Verify sensor icon color changes with alert levels
- [ ] Test `formatted_content` attribute (full details)
- [ ] Test `formatted_summary` attribute (compact icons)
- [ ] Verify no switch entities created
- [ ] Test with Norwegian language
- [ ] Test with English language

---

## Questions?

If you need to revert these changes, the switch functionality can be restored from git history. However, the new approach is recommended for its simplicity and flexibility.
