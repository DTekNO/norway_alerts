# Avalanche Warning Display Examples

This document shows how to display the rich avalanche-specific attributes in Home Assistant cards and templates, which differs significantly from the simple landslide/flood warning displays.

**Note**: Each alert includes an `entity_picture` attribute with the official Yr.no warning icon that matches the danger level and warning type. These can be displayed in templates using `<img>` tags.

## Simple Display Template

For a basic avalanche warning card:

```yaml
type: markdown
content: >
  ## <img src="{{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].entity_picture }}" width="24" height="24"> {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].region_name }}
  
  **Danger Level:** {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].danger_level_name }}  
  **Valid:** {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].valid_from | as_timestamp | timestamp_custom('%d/%m %H:%M') }} - {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].valid_to | as_timestamp | timestamp_custom('%d/%m %H:%M') }}
  
  ### Main Warning
  {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].main_text }}
  
  ### Current Conditions
  **Snow Surface:** {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].snow_surface | truncate(150) }}
  
  **Weak Layers:** {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].current_weaklayers | truncate(150) }}
  
  ---
  *Issued by: {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].forecaster }}*
```

### Alternative: Using Emoji Instead of Icons

If you prefer emoji over the official warning icons:

```yaml
type: markdown
content: >
  ## 🏔️ Avalanche Warning: {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].region_name }}
  
  **Danger Level:** {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].danger_level_name }}  
  **Valid:** {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].valid_from | as_timestamp | timestamp_custom('%d/%m %H:%M') }} - {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].valid_to | as_timestamp | timestamp_custom('%d/%m %H:%M') }}
```

## Detailed Display Template

For a comprehensive avalanche information display:

```yaml
type: markdown
content: >
  # 🏔️ Avalanche Warnings - Vestland
  
  {% for alert in states.sensor.varsom_avalanche_vestland.attributes.alerts %}
  ## <img src="{{ alert.entity_picture }}" width="32" height="32"> {{ alert.region_name }}
  
  ### {{ alert.danger_level_name }}
  
  **Valid Period:** {{ alert.valid_from | as_timestamp | timestamp_custom('%A %d %B, %H:%M') }} - {{ alert.valid_to | as_timestamp | timestamp_custom('%A %d %B, %H:%M') }}
  
  #### 📢 Main Warning
  {{ alert.main_text }}
  
  {% if alert.emergency_warning and alert.emergency_warning != "Not given" %}
  #### 🚨 Emergency Warning  
  {{ alert.emergency_warning }}
  {% endif %}
  
  {% if alert.avalanche_danger %}
  #### ⚡ Avalanche Danger Assessment
  {{ alert.avalanche_danger | truncate(200) }}...
  {% endif %}
  
  #### ❄️ Snow Conditions
  {% if alert.snow_surface %}
  **Surface:** {{ alert.snow_surface | truncate(150) }}...
  {% endif %}
  
  {% if alert.current_weaklayers %}
  **Weak Layers:** {{ alert.current_weaklayers | truncate(150) }}...
  {% endif %}
  
  #### 📊 Recent Activity & Observations
  {% if alert.latest_avalanche_activity %}
  **Recent Avalanches:** {{ alert.latest_avalanche_activity | truncate(120) }}...
  {% endif %}
  
  {% if alert.latest_observations %}
  **Field Observations:** {{ alert.latest_observations | truncate(120) }}...
  {% endif %}
  
  #### 🎯 Avalanche Problems ({{ alert.avalanche_problems | length }})
  {% for problem in alert.avalanche_problems %}
  **{{ problem.AvalancheExtName }}** - {{ problem.AvalCauseName }} ({{ problem.AvalProbabilityName }})
  {% if problem.AvalancheExtName == "Dry slab avalanche" %}🎿{% elif problem.AvalancheExtName == "Wet avalanche" %}💧{% else %}⚠️{% endif %}
  {% endfor %}
  
  #### 🛡️ Safety Advice ({{ alert.avalanche_advices | length }})
  {% for advice in alert.avalanche_advices %}
  **{{ loop.index }}.** {{ advice.Text | truncate(100) }}...
  {% endfor %}
  
  {% if alert.wind_speed or alert.temperature %}
  #### 🌤️ Mountain Weather
  **Wind:** {{ alert.wind_speed }} {{ alert.wind_direction }} | **Temp:** {{ alert.temperature }}°C | **Precip:** {{ alert.precipitation }}
  {% endif %}
  
  **Elevation:** {{ alert.exposed_height }}m+ | **Forecaster:** {{ alert.forecaster }} | **Region:** {{ alert.region_id }}
  
  ---
  {% endfor %}
  
  *Total: {{ states.sensor.varsom_avalanche_vestland.attributes.alerts | length }} avalanche regions*
```

## Comparison: Landslide vs Avalanche Display

### Landslide/Flood Warning (Simple)
```yaml
content: >
  ## 🌊 Flood Warning: {{ states.sensor.varsom_flood_vestland.attributes.alerts[0].area_name }}
  
  **Level:** {{ states.sensor.varsom_flood_vestland.attributes.alerts[0].danger_level }}
  
  ### Warning
  {{ states.sensor.varsom_flood_vestland.attributes.alerts[0].warning_text }}
  
  ### Advice  
  {{ states.sensor.varsom_flood_vestland.attributes.alerts[0].advice_text }}
  
  ### Consequences
  {{ states.sensor.varsom_flood_vestland.attributes.alerts[0].consequence_text }}
```

### Avalanche Warning (Rich Data)
```yaml
content: >
  ## 🏔️ Avalanche Warning: {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].region_name }}
  
  **Level:** {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].danger_level_name }}
  
  ### Main Warning
  {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].main_text }}
  
  ### Technical Assessment
  {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].avalanche_danger }}
  
  ### Snow Analysis
  **Surface:** {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].snow_surface | truncate(100) }}
  **Weak Layers:** {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].current_weaklayers | truncate(100) }}
  
  ### Problems ({{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].avalanche_problems | length }})
  {% for problem in states.sensor.varsom_avalanche_vestland.attributes.alerts[0].avalanche_problems %}
  • **{{ problem.AvalancheExtName }}** ({{ problem.AvalProbabilityName }})
  {% endfor %}
  
  ### Safety Advice ({{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].avalanche_advices | length }})
  {% for advice in states.sensor.varsom_avalanche_vestland.attributes.alerts[0].avalanche_advices %}
  {{ loop.index }}. {{ advice.Text }}
  {% endfor %}
```

## Dashboard Card Examples

### Compact Avalanche Card
```yaml
type: entities
title: Current Avalanche Conditions
entities:
  - entity: sensor.varsom_avalanche_vestland
    type: custom:template-entity-row
    name: "{{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].region_name }}"
    secondary: "{{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].danger_level_name }}"
    icon: "{{ states.sensor.varsom_avalanche_vestland.attributes.entity_picture }}"
```

### Avalanche Problem Summary
```yaml
type: markdown
title: Avalanche Problems Today
content: >
  {% for problem in states.sensor.varsom_avalanche_vestland.attributes.alerts[0].avalanche_problems %}
  ### {{ problem.AvalancheExtName }}
  **Cause:** {{ problem.AvalCauseName }}  
  **Likelihood:** {{ problem.AvalProbabilityName }}  
  **Triggering:** {{ problem.AvalTriggerSimpleName }}
  
  {% endfor %}
```

### Mountain Conditions Card
```yaml
type: vertical-stack
cards:
  - type: markdown
    content: >
      ## ❄️ Current Snow Conditions
      {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].snow_surface }}
      
      ## 🔍 Weak Layers Analysis  
      {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].current_weaklayers }}
      
      ## 📊 Recent Activity
      {{ states.sensor.varsom_avalanche_vestland.attributes.alerts[0].latest_observations }}
```

## Key Differences from Landslide/Flood

1. **Structured Data**: Avalanche warnings have arrays of problems and advice vs simple text fields
2. **Technical Detail**: Snow analysis, weak layers, and mountain weather vs generic consequences  
3. **Visual Elements**: Advice includes images and icons vs plain text
4. **Professional Terminology**: Uses avalanche-specific terms and danger scale
5. **Multiple Information Sources**: Problems, observations, weather impact vs single warning text

The avalanche display templates can leverage this rich structured data to provide much more useful and actionable information for backcountry users compared to the generic warning text used by landslide and flood warnings.