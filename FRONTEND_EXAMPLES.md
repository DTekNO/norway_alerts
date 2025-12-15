# Frontend Display Examples for Varsom Alerts

## Basic Entity Card

Shows the alert level and count:

```yaml
type: entities
title: Landslide Warnings
entities:
  - entity: sensor.varsom_landslide_vestland
    name: Alert Level
    type: attribute
    attribute: highest_level
  - entity: sensor.varsom_landslide_vestland
    name: Active Alerts
    type: attribute
    attribute: active_alerts
```

## Alert List with Markdown Card

Display all alerts with details:

```yaml
type: markdown
title: Varsom Landslide Alerts
content: |
  {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
  {% if alerts and alerts|length > 0 %}
    {% for alert in alerts %}
  **Alert {{ loop.index }}: Level {{ alert.level_name|upper }}**
  - **Municipalities**: {{ alert.municipalities|join(', ') }}
  - **Valid**: {{ alert.valid_from[:10] }} to {{ alert.valid_to[:10] }}
  - **Warning**: {{ alert.main_text[:200] }}...
  - [View on Varsom.no]({{ alert.url }})
  ---
    {% endfor %}
  {% else %}
  ✅ No active warnings
  {% endif %}
```

## Filtered Municipality View

Show only specific municipalities within the alerts:

```yaml
type: markdown
title: My Area Alerts (Tysnes/Bergen)
content: |
  {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
  {% set my_munis = ['Tysnes', 'Bergen'] %}
  {% if alerts and alerts|length > 0 %}
    {% for alert in alerts %}
      {% set matching_munis = alert.municipalities | select('in', my_munis) | list %}
      {% if matching_munis|length > 0 %}
  **{{ alert.level_name|upper }} Alert**
  - **Affects YOUR area**: {{ matching_munis|join(', ') }}
  - **Also affects**: {{ (alert.municipalities | reject('in', my_munis) | list)[:3]|join(', ') }}{% if (alert.municipalities | reject('in', my_munis) | list)|length > 3 %}, and {{ (alert.municipalities | reject('in', my_munis) | list)|length - 3 }} more{% endif %}
  - **Warning**: {{ alert.warning_text[:150] }}...
  - [Details & Map]({{ alert.url }})
  ---
      {% endif %}
    {% endfor %}
  {% else %}
  ✅ No alerts affecting your area
  {% endif %}
```

## Conditional Alert Card (only when active)

```yaml
type: conditional
conditions:
  - entity: sensor.varsom_landslide_vestland
    state_not: "1"
card:
  type: markdown
  title: ⚠️ ACTIVE LANDSLIDE WARNING
  content: |
    {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
    {% set alert = alerts[0] %}
    **Level: {{ alert.level_name|upper }}**
    
    {{ alert.main_text }}
    
    **Affected municipalities**: {{ alert.municipalities|join(', ') }}
    
    **Valid until**: {{ alert.valid_to }}
    
    [View Map on Varsom.no]({{ alert.url }})
```

## Glance Card with Icon

```yaml
type: glance
title: Warning Status
entities:
  - entity: sensor.varsom_landslide_vestland
    name: Landslide
    icon: mdi:landslide
  - entity: sensor.varsom_flood_vestland
    name: Flood
    icon: mdi:home-flood
columns: 2
```

## Custom Button Card (requires custom:button-card)

```yaml
type: custom:button-card
entity: sensor.varsom_landslide_vestland
name: Landslide Warnings
show_state: false
show_icon: true
tap_action:
  action: url
  url_path: |
    [[[
      const alerts = entity.attributes.alerts;
      return alerts && alerts.length > 0 ? alerts[0].url : 'https://www.varsom.no/';
    ]]]
state_display: |
  [[[
    const level = entity.attributes.highest_level;
    const count = entity.attributes.active_alerts;
    return count > 0 ? `${count} ${level} alert(s)` : 'No alerts';
  ]]]
styles:
  card:
    - background: |
        [[[
          const level = entity.state;
          if (level == '4') return 'darkred';
          if (level == '3') return 'darkorange';
          if (level == '2') return 'gold';
          return 'green';
        ]]]
```

## Template Sensor for Specific Municipality

Create this in your `configuration.yaml`:

```yaml
template:
  - sensor:
      - name: "Tysnes Landslide Alert"
        unique_id: tysnes_landslide_alert
        state: |
          {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
          {% if alerts %}
            {% set tysnes_alerts = alerts | selectattr('municipalities', 'search', 'Tysnes') | list %}
            {% if tysnes_alerts %}
              {{ tysnes_alerts[0].level_name }}
            {% else %}
              green
            {% endif %}
          {% else %}
            green
          {% endif %}
        attributes:
          count: |
            {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
            {% if alerts %}
              {{ alerts | selectattr('municipalities', 'search', 'Tysnes') | list | length }}
            {% else %}
              0
            {% endif %}
          alerts: |
            {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
            {% if alerts %}
              {{ alerts | selectattr('municipalities', 'search', 'Tysnes') | list }}
            {% else %}
              []
            {% endif %}
```

## Mobile Notification Automation

```yaml
automation:
  - alias: "Landslide Warning Notification"
    trigger:
      - platform: state
        entity_id: sensor.varsom_landslide_vestland
        to: "2"  # Yellow
      - platform: state
        entity_id: sensor.varsom_landslide_vestland
        to: "3"  # Orange
      - platform: state
        entity_id: sensor.varsom_landslide_vestland
        to: "4"  # Red
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ Landslide Warning"
          message: |
            Level: {{ state_attr('sensor.varsom_landslide_vestland', 'highest_level')|upper }}
            
            {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
            {% set my_alerts = alerts | selectattr('municipalities', 'search', 'Tysnes|Bergen') | list %}
            {% if my_alerts %}
            Affects your area: {{ my_alerts[0].municipalities|join(', ') }}
            {{ my_alerts[0].main_text }}
            {% else %}
            {{ alerts[0].main_text }}
            {% endif %}
          data:
            url: |
              {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
              {{ alerts[0].url if alerts else 'https://www.varsom.no/' }}
            tag: varsom_alert
            importance: high
```

## Dashboard Layout Example

```yaml
type: vertical-stack
cards:
  # Status overview
  - type: glance
    title: Warning Status
    entities:
      - entity: sensor.varsom_landslide_vestland
        name: Landslide
      - entity: sensor.varsom_flood_vestland
        name: Flood
  
  # Show details when active
  - type: conditional
    conditions:
      - entity: sensor.varsom_landslide_vestland
        state_not: "1"
    card:
      type: markdown
      title: Active Landslide Warnings
      content: |
        {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') %}
        {% for alert in alerts %}
        ### {{ alert.level_name|upper }} - {{ alert.danger_type }}
        **Your areas**: {{ alert.municipalities | select('in', ['Tysnes', 'Bergen']) | list | join(', ') }}
        
        {{ alert.warning_text }}
        
        [View on Varsom.no]({{ alert.url }})
        ---
        {% endfor %}
```

---

## Understanding the Data

When you look at `sensor.varsom_landslide_vestland` in Developer Tools → States, you'll see:

- **State**: `1`, `2`, `3`, or `4` (alert level)
- **Attributes**:
  - `active_alerts`: Number of active warnings
  - `highest_level`: Text version (green/yellow/orange/red)
  - `alerts`: Array of alert objects
  - `municipality_filter`: Your filter (if set)

Each alert object contains:
- `level`: Numeric level
- `level_name`: Color name
- `municipalities`: Array of affected municipalities
- `main_text`, `warning_text`, `advice_text`: Warning details
- `url`: Link to Varsom.no with map
