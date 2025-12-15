# Complete Dashboard Setup for Tysnes/Bergen Area

## Step 1: Template Sensors (configuration.yaml)

Add these to your `configuration.yaml`:

```yaml
template:
  - sensor:
      # Combined sensor for your area
      - name: "My Area Landslide Alert"
        unique_id: my_area_landslide
        state: |
          {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
          {% if alerts %}
            {% set my_alerts = alerts | selectattr('municipalities', 'search', 'Tysnes|Bergen') | list %}
            {{ my_alerts[0].level_name if my_alerts else 'green' }}
          {% else %}
            green
          {% endif %}
        attributes:
          alert_count: |
            {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
            {{ (alerts | selectattr('municipalities', 'search', 'Tysnes|Bergen') | list | length) if alerts else 0 }}
          my_municipalities: |
            {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
            {% if alerts %}
              {% set my_alerts = alerts | selectattr('municipalities', 'search', 'Tysnes|Bergen') | list %}
              {% if my_alerts %}
                {% set my_munis = namespace(list=[]) %}
                {% for alert in my_alerts %}
                  {% for muni in alert.municipalities %}
                    {% if 'Tysnes' in muni or 'Bergen' in muni %}
                      {% set my_munis.list = my_munis.list + [muni] %}
                    {% endif %}
                  {% endfor %}
                {% endfor %}
                {{ my_munis.list | unique | list }}
              {% else %}
                []
              {% endif %}
            {% else %}
              []
            {% endif %}
          summary: |
            {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
            {% if alerts %}
              {% set my_alerts = alerts | selectattr('municipalities', 'search', 'Tysnes|Bergen') | list %}
              {% if my_alerts %}
                {% set count = my_alerts | length %}
                {% set level = my_alerts[0].level_name %}
                {{ count }} {{ level }} alert(s) affecting your area
              {% else %}
                No alerts for your area
              {% endif %}
            {% else %}
              No data
            {% endif %}
        icon: >
          {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
          {% if alerts %}
            {% set my_alerts = alerts | selectattr('municipalities', 'search', 'Tysnes|Bergen') | list %}
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
```

Restart Home Assistant after adding this.

## Step 2: Dashboard Card - Recommended Option

```yaml
type: vertical-stack
cards:
  # Status at a glance
  - type: entities
    title: Varsom Warnings
    entities:
      - entity: sensor.my_area_landslide_alert
        name: My Area (Tysnes/Bergen)
        secondary_info: last-changed
      - type: attribute
        entity: sensor.my_area_landslide_alert
        attribute: summary
        name: Status
  
  # Show details when there's an alert
  - type: conditional
    conditions:
      - entity: sensor.my_area_landslide_alert
        state_not: "green"
    card:
      type: markdown
      title: ⚠️ Active Warnings for Your Area
      content: |
        {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
        {% if alerts %}
          {% for alert in alerts %}
            {% set my_munis = [] %}
            {% for m in alert.municipalities %}
              {% if 'Tysnes' in m or 'Bergen' in m %}
                {% set my_munis = my_munis + [m] %}
              {% endif %}
            {% endfor %}
            {% if my_munis|length > 0 %}
        ### {{ alert.level_name|upper }} Alert
        
        **YOUR AREAS**: {{ my_munis|join(', ') }}
        
        {{ alert.main_text }}
        
        **Valid**: {{ alert.valid_from[:16] }} to {{ alert.valid_to[:16] }}
        
        [📍 View Map]({{ alert.url }})
        
        <details>
        <summary>All affected areas</summary>
        {{ alert.municipalities|join(', ') }}
        </details>
        
        ---
            {% endif %}
          {% endfor %}
        {% endif %}
```

This setup gives you:
- ✅ Clean display showing only YOUR affected areas
- ✅ Full alert details when warnings are active
- ✅ Links to Varsom.no maps
- ✅ Collapsible view of all affected areas
