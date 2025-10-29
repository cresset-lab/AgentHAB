# Example Rules

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

```text
rule "Evening scene at sunset"
when
    Channel astro:sun:home:set#event triggered START
then
    sendCommand(LivingRoom_Lights, 50)
    sendCommand(Blinds, DOWN)
end
```




