# Varsom Notification System

The Varsom integration now supports sending notifications to the Home Assistant notification bus when alert status changes. This allows notifications to be pushed to the HA companion app and other notification systems.

## Configuration Options

### Enable Notifications
- **Type**: Boolean (True/False)
- **Default**: False
- **Description**: Whether to send notifications for alert changes

### Notification Severity
- **Type**: Dropdown selection
- **Options**: 
  - "All warnings" - Notify for all warning levels (green, yellow, orange, red, black)
  - "Yellow and above" - Notify only for yellow, orange, red, black warnings
  - "Orange and above" - Notify only for orange, red, black warnings  
  - "Red warnings only" - Notify only for red and black warnings
- **Default**: "Yellow and above"

## Notification Types

### New Alert Notification
```
🟡 New Avalanche Warning
Bergen - Moderate danger level

Snow conditions have deteriorated. Increased avalanche danger...
```

### Upgraded Alert Notification
```
🔴 Upgraded Flood Warning
Oslo - High danger level

Water levels continue to rise. Immediate evacuation recommended...
```

### Resolved Alert Notification
```
✅ Resolved Landslide Warning
Stavanger - Warning no longer active
```

## Notification Behavior

- **New Alerts**: Sent when a warning first appears for a region
- **Severity Changes**: Sent when danger level increases (e.g., yellow to orange)
- **Resolved Alerts**: Sent when a warning is no longer active
- **Filtering**: Only sends notifications that meet the configured severity threshold
- **Unique IDs**: Each notification has a unique ID to prevent duplicates

## Integration with Home Assistant

Notifications appear in:
- **Persistent Notifications**: Visible in HA interface 
- **HA Companion App**: Push notifications on mobile devices
- **Custom Notification Services**: Can be forwarded to other services via automations

## Example Automation

You can create automations that respond to Varsom notification events:

```yaml
automation:
  - alias: "Forward Varsom Alerts to Slack"
    trigger:
      platform: event
      event_type: persistent_notifications_updated
    condition:
      condition: template
      value_template: "{{ 'varsom_' in trigger.event.data.notification_id }}"
    action:
      service: notify.slack
      data:
        message: "{{ trigger.event.data.message }}"
        title: "{{ trigger.event.data.title }}"
```

## Setup Instructions

1. **Enable in Configuration**: When setting up a Varsom sensor, check "Enable Notifications"
2. **Choose Severity**: Select the minimum warning level for notifications
3. **Test**: Toggle test mode to generate sample alerts and verify notifications work
4. **Monitor**: Notifications will appear when real alerts change status

## Technical Details

- **Update Frequency**: Checks for changes every 30 minutes (same as data updates)
- **State Tracking**: Compares current vs previous alert states to detect changes
- **Error Handling**: Failed notifications are logged but don't affect sensor operation
- **Performance**: Minimal overhead - only processes notifications when alerts actually change