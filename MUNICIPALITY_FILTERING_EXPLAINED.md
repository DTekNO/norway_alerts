# Municipality Filtering - How It Works

## The Issue You're Experiencing

**What you see**: Setting filter to "Tysnes, Bergen" but still seeing Askøy, Høyanger, etc. in the alerts

**Why this happens**: A single NVE warning often covers multiple municipalities at once.

### Example Alert
```yaml
Alert #584731:
  level: Yellow (2)
  municipalities: [Askøy, Bergen, Bømlo, Fitjar, Høyanger, Kvam, Samnanger, Stord, Tysnes, Vaksdal]
```

When you filter for "Tysnes, Bergen":
- ✅ This alert DOES affect Tysnes (match!)
- ✅ This alert DOES affect Bergen (match!)  
- ❌ But it ALSO affects 8 other municipalities

**The filter is working** - it's showing you alerts that affect your areas. Those alerts just happen to cover a wider region.

## Solutions

### Solution 1: Better Frontend Display (RECOMMENDED)

Use the frontend examples to show ONLY your municipalities within each alert:

```yaml
type: markdown
title: Alerts for MY Municipality
content: |
  {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
  {% set my_areas = ['Tysnes', 'Bergen'] %}
  {% if alerts %}
    {% for alert in alerts %}
      {% set my_affected = alert.municipalities | select('in', my_areas) | list %}
      {% if my_affected|length > 0 %}
  **Level {{ alert.level_name|upper }}**
  - **AFFECTS YOU**: {{ my_affected|join(', ') }}
  - Also: {{ (alert.municipalities | reject('in', my_areas) | list)[:3]|join(', ') }}...
  - {{ alert.main_text[:100] }}...
  - [Map]({{ alert.url }})
  ---
      {% endif %}
    {% endfor %}
  {% else %}
  ✅ No warnings
  {% endif %}
```

This shows:
- ✅ Which of YOUR areas are affected
- ✅ A preview of other areas (so you know it's regional)
- ✅ Only alerts that actually affect your filter

### Solution 2: Template Sensor for Each Municipality

Create dedicated sensors in `configuration.yaml`:

```yaml
template:
  - sensor:
      # Sensor for Tysnes only
      - name: "Tysnes Landslide Alert"
        unique_id: tysnes_landslide
        state: |
          {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
          {% if alerts %}
            {% set my_alerts = alerts | selectattr('municipalities', 'search', 'Tysnes') | list %}
            {{ my_alerts[0].level_name if my_alerts else 'green' }}
          {% else %}
            green
          {% endif %}
        attributes:
          count: |
            {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
            {{ (alerts | selectattr('municipalities', 'search', 'Tysnes') | list | length) if alerts else 0 }}
          municipalities_affected: |
            {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
            {% if alerts %}
              {% set my_alerts = alerts | selectattr('municipalities', 'search', 'Tysnes') | list %}
              {% if my_alerts %}
                {% set all_munis = [] %}
                {% for alert in my_alerts %}
                  {% set all_munis = all_munis + alert.municipalities %}
                {% endfor %}
                {{ all_munis | unique | list }}
              {% else %}
                []
              {% endif %}
            {% else %}
              []
            {% endif %}
          warnings: |
            {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
            {% if alerts %}
              {{ alerts | selectattr('municipalities', 'search', 'Tysnes') | list }}
            {% else %}
              []
            {% endif %}
        icon: >
          {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
          {% if alerts %}
            {% set my_alerts = alerts | selectattr('municipalities', 'search', 'Tysnes') | list %}
            {% if my_alerts %}
              {% set level = my_alerts[0].level %}
              {% if level == 4 %}mdi:alert-octagon
              {% elif level == 3 %}mdi:alert
              {% elif level == 2 %}mdi:alert-circle
              {% else %}mdi:check-circle{% endif %}
            {% else %}
              mdi:check-circle
            {% endif %}
          {% else %}
            mdi:check-circle
          {% endif %}

      # Sensor for Bergen only
      - name: "Bergen Landslide Alert"
        unique_id: bergen_landslide
        state: |
          {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
          {% if alerts %}
            {% set my_alerts = alerts | selectattr('municipalities', 'search', 'Bergen') | list %}
            {{ my_alerts[0].level_name if my_alerts else 'green' }}
          {% else %}
            green
          {% endif %}
```

Then use these sensors in your dashboard:
```yaml
type: entities
entities:
  - sensor.tysnes_landslide_alert
  - sensor.bergen_landslide_alert
```

### Solution 3: Strict Filter (Show ONLY Your Municipalities)

If you want to see ONLY alerts that affect EXCLUSIVELY your municipalities (not showing alerts that also affect others), I can modify the filter logic. However, this might miss important warnings because NVE alerts typically cover regions, not single municipalities.

### Solution 4: Location-Based Auto-Detection

I've created `municipality_lookup.py` which can automatically determine your municipality from Home Assistant's lat/lon coordinates. Would you like me to:

1. ✅ Integrate this into the config flow?
2. ✅ Allow users to provide their own GeoJSON boundaries for precise lookup?
3. ✅ Auto-set the municipality filter based on HA location?

## Understanding NVE Alert Geography

NVE doesn't issue municipality-specific warnings. They issue warnings like:

- "Western coastal areas of Vestland" → 10-15 municipalities
- "Inner fjord areas" → 5-8 municipalities  
- "Bergen and surrounding areas" → Bergen + neighbors

This is why filtering can never show "only Tysnes" - the warnings are inherently regional.

## Recommended Approach

**For your use case (Tysnes area):**

1. Keep integration filtering: `Tysnes, Bergen` (catches relevant alerts)
2. Use Frontend markdown card to show: "Affects: Tysnes (and 8 other areas)"
3. Create template sensor for Tysnes-specific view
4. Set up automation to notify when Tysnes appears in any alert

This gives you:
- ✅ All relevant warnings (nothing missed)
- ✅ Clear visibility of what affects YOUR area
- ✅ Context about regional scope
- ✅ Specific alerts for your location

Would you like me to:
1. Create a complete example dashboard configuration for you?
2. Implement the location-based auto-detection?
3. Add GeoJSON boundary support?
