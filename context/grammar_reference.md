# Grammar Reference (openHAB Rules DSL)

This summarizes the main constructs used in the openHAB *Textual Rules* / *Rules DSL*,
based on the official documentation.

## Rule File Structure

- **Location**: rules live in `$OPENHAB_CONF/rules/*.rules`.
- A rule file may contain:
  - **Imports**
  - **File-global variables** (shared by all rules in the file)
  - **Rule definitions**

```text
import java.util.Date

var Number counter = 0

rule "Example Rule"
when
    Item MyItem changed
then
    counter = counter + 1
    logInfo("Example", "MyItem changed " + counter + " times.")
end
```

## Rule Definition

- **Syntax**: `rule "<name>" [@tag1 @tag2 ...]`
  - `when` block: one or more triggers (OR-ed).
  - `then` block: script to execute.

```text
rule "My Rule Name"
when
    <trigger-1>
    or
    <trigger-2>
then
    // actions
end
```

## Triggers

- **Item event triggers**
  - `Item <ItemName> changed`
  - `Item <ItemName> changed to <State>`
  - `Item <ItemName> received command`
  - `Item <ItemName> received command <Command>`
  - `Item <ItemName> updated`

- **Channel triggers**
  - `Channel '<binding:thing:channel>' triggered`
  - `Channel '<binding:thing:channel>' triggered <Event>`

- **Time-based triggers**
  - `Time cron "<cron expression>"`
  - `Time is midnight` (and other daily convenience expressions in newer versions)

- **System triggers**
  - `System started`
  - `System shuts down`

Examples:

```text
when
    Item MotionSensor changed to ON
then
    // ...
end
```

```text
when
    Time cron "0 0 7 * * ?"
then
    // runs daily at 07:00
end
```

```text
when
    Channel 'astro:sun:home:set#event' triggered START
then
    // sunset action
end
```

## Conditions and Expressions

- `if (<condition>) { ... } else { ... }`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `&&`, `||`, `!`

```text
if (Light_Switch.state != ON) {
    Light_Switch.sendCommand(ON)
}
```

## Actions (Common APIs)

- **Commands and updates**
  - `sendCommand(<Item>, <Value>)`
  - `<Item>.sendCommand(<Value>)`
  - `postUpdate(<Item>, <Value>)`
  - `<Item>.postUpdate(<Value>)`

- **Timers**
  - `createTimer(<ZonedDateTime>, [ | ... ])`
  - Typical usage: `createTimer(now.plusSeconds(10), [ | <code> ])`

```text
createTimer(now.plusMinutes(5), [ |
    Light.sendCommand(OFF)
])
```

- **Logging**
  - `logDebug("tag", "message")`
  - `logInfo("tag", "message")`
  - `logWarn("tag", "message")`
  - `logError("tag", "message")`

```text
logInfo("rules.example", "Rule executed, current state = " + MyItem.state)
```

## Item States and Types

- Access state via `<Item>.state`.
- States are typed (e.g., `OnOffType`, `OpenClosedType`, `Number`, `DateTime`).
- Type conversion helpers:
  - `(<NumberItem>.state as Number).intValue`
  - `(<NumberItem>.state as DecimalType).toBigDecimal`

```text
val currentTemp = (Temperature.state as Number).floatValue
if (currentTemp > 25.0) {
    Fan.sendCommand(ON)
}
```

## Implicit Variables

Available in the `then` block depending on the trigger:

- `receivedCommand` – command that triggered a `received command` rule.
- `previousState` / `newState` – for `changed` triggers.
- `triggeringItem` – the `Item` that triggered the rule (for item-based triggers).
- `receivedEvent` – string for channel trigger events.

```text
rule "Log received command"
when
    Item LivingRoom_Light received command
then
    logInfo("rules.example", "Command " + receivedCommand + " for " + triggeringItem.name)
end
```

```text
rule "Log state change"
when
    Item Temperature changed
then
    logInfo("rules.example", "Temperature changed from " + previousState + " to " + newState)
end
```
