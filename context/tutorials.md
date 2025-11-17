# Tutorials (openHAB Rules DSL)

These short, text-focused tutorials mirror the official openHAB *Textual Rules* /
*Rules DSL* documentation and are designed to be good LLM context.

---

## 1. First Rule: Turn on a Light When Motion is Detected

**Goal**: When a motion sensor detects motion, turn on a light.

**Prerequisites**
- Items defined (in `*.items`):
  - `MotionSensor` (e.g., `Switch MotionSensor "Motion"`).
  - `Light_Switch` (e.g., `Switch Light_Switch "Light"`).

**Rule**

```text
rule "Turn on light when motion detected"
when
    Item MotionSensor changed to ON
then
    if (Light_Switch.state != ON) {
        sendCommand(Light_Switch, ON)
    }
end
```

**Explanation**
- `when Item MotionSensor changed to ON`: trigger when the motion sensor changes to `ON`.
- `if (Light_Switch.state != ON)`: avoid redundant commands.
- `sendCommand(Light_Switch, ON)`: equivalent to `Light_Switch.sendCommand(ON)` in DSL.

---

## 2. Scheduled Rule: Turn Off Lights at Midnight

**Goal**: Turn off a light every night at midnight using a cron trigger.

**Prerequisites**
- Item:
  - `LightSwitch` (switch-type item).

**Rule**

```text
rule "Turn off Lights at Midnight"
when
    Time cron "0 0 0 * * ?"
then
    LightSwitch.sendCommand(OFF)
end
```

**Explanation**
- `Time cron "0 0 0 * * ?"`: standard Quartz cron expression for midnight every day.
- Sends the `OFF` command to `LightSwitch` at that time.

---

## 3. Using Astro Binding: Evening Scene at Sunset

**Goal**: At sunset, set a cozy evening scene by dimming lights and closing blinds.

**Prerequisites**
- Astro binding configured with a `sun` thing (e.g., `astro:sun:home`).
- Items:
  - `LivingRoom_Lights` (dimmable item).
  - `Blinds` (rollershutter or switch-like item).

**Rule**

```text
rule "Evening scene at sunset"
when
    Channel 'astro:sun:home:set#event' triggered START
then
    sendCommand(LivingRoom_Lights, 50)
    sendCommand(Blinds, DOWN)
end
```

**Explanation**
- Astro exposes a channel `astro:sun:home:set#event` which triggers events like `START`.
- The rule listens for the `START` event and then:
  - Sets `LivingRoom_Lights` to 50% brightness.
  - Closes `Blinds` by sending `DOWN`.

---

## 4. Delay with Timers: Turn Off Light After Motion

**Goal**: Turn on a light when motion is detected and turn it off 5 minutes later if no more motion occurs.

**Prerequisites**
- Items:
  - `MotionSensor`
  - `Light`

**Rule**

```text
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

**Explanation**
- `createTimer(now.plusMinutes(5), [ | ... ])`: schedules a block to run in five minutes.
- Inside the timer block, we check `MotionSensor.state` again:
  - If it is not `ON`, we send `OFF` to `Light`.

---

## 5. Using Implicit Variables: Logging Commands and State Changes

**Goal**: Demonstrate how to use `receivedCommand`, `triggeringItem`, `previousState`, and `newState`.

**Rule: Log Commands**

```text
rule "Log received command"
when
    Item LivingRoom_Light received command
then
    logInfo("rules.tutorial", "Command " + receivedCommand + " for " + triggeringItem.name)
end
```

**Rule: Log State Changes**

```text
rule "Log state change"
when
    Item Temperature changed
then
    logInfo("rules.tutorial", "Temperature changed from " + previousState + " to " + newState)
end
```

**Explanation**
- `receivedCommand`: command that triggered the rule.
- `triggeringItem`: item that caused the trigger.
- `previousState` / `newState`: states around an `Item ... changed` trigger.

---

## 6. Initialization: Run Logic When openHAB Starts

**Goal**: Initialize some item states or timers when the system starts.

**Rule**

```text
rule "Initialize at system start"
when
    System started
then
    logInfo("rules.tutorial", "System started; initializing")
    // Example: post initial values
    // SomeCounter.postUpdate(0)
    // SomeSwitch.sendCommand(OFF)
end
```

**Explanation**
- `System started` runs when the automation engine starts (e.g., after a restart).
- Useful for resetting counters, restoring states, or scheduling timers.
