# openHAB Rule DSL Quick Syntax

- rule "Name"
- when <trigger>
- then <actions>
- end

Common triggers:
- Item <ItemName> changed
- Item <ItemName> received command ON/OFF
- Time cron "<expression>"

Examples of actions:
- if (<condition>) { ... }
- sendCommand(<ItemName>, <Value>)
- postUpdate(<ItemName>, <Value>)
- logInfo("tag", "message")

Notes:
- Use `Number`, `Switch`, `Contact`, `String` item types appropriately.
- Use `System started` trigger for initialization.




