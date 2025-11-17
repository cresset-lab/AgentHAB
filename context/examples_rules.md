# Example Rules (openHAB Rules DSL)

The snippets below are taken from and aligned with the official openHAB
*Textual Rules* / *Rules DSL* documentation.

Each example is wrapped in a `text` code block so it can be used directly
as context for LLM prompts and rule generation.

---

```text
// Basic item-triggered rule with a simple condition
rule "Turn on light when motion detected"
when
    Item MotionSensor changed to ON
then
    if (Light_Switch.state != ON) {
        sendCommand(Light_Switch, ON)
    }
end
```

```text
// Scene rule using Astro binding sunset channel
rule "Evening scene at sunset"
when
    Channel 'astro:sun:home:set#event' triggered START
then
    sendCommand(LivingRoom_Lights, 50)
    sendCommand(Blinds, DOWN)
end
```

```text
// Reacting to Astro sunrise events with receivedEvent
rule "Start wake up light on sunrise"
when
    Channel 'astro:sun:home:rise#event' triggered
then
    switch(receivedEvent) {
        case "START": {
            Light.sendCommand(ON)
        }
    }
end
```

```text
// Using a cron trigger for scheduled actions
rule "Turn off lights at midnight"
when
    Time cron "0 0 0 * * ?"
then
    LightSwitch.sendCommand(OFF)
end
```

```text
// Using imports, a file-global variable, and logging
import java.util.Date

var Number counter = 0

rule "Count item updates"
when
    Item MyItem changed
then
    counter = counter + 1
    logInfo("rules.example", "MyItem changed " + counter + " times. Last change at " + new Date)
end
```

```text
// Using implicit variables: triggeringItem and receivedCommand
rule "Log received command"
when
    Item LivingRoom_Light received command
then
    logInfo("rules.example", "Received command " + receivedCommand + " for " + triggeringItem.name)
end
```

```text
// Using timers for delayed actions
rule "Turn off light after motion"
when
    Item MotionSensor changed to ON
then
    Light.sendCommand(ON)
    createTimer(now.plusMinutes(5), [ |
        if (MotionSensor.state != ON) {
            Light.sendCommand(OFF)
        }
    ])
end
```

```text
// Rule triggered when the system starts
rule "Initialize at system start"
when
    System started
then
    logInfo("rules.example", "System started; initializing states")
    // e.g. postUpdate(SomeItem, 0)
end
```
