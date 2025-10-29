# Grammar Reference (DSL)

- rule: `rule "<name>" ... end`
- triggers:
  - `Item <ItemName> changed [to <state>]`
  - `Item <ItemName> received command <command>`
  - `Time cron "<expr>"`
  - `System started`
- conditions: `if (<expr>) { ... }`
- actions:
  - `sendCommand(<Item>, <Value>)`
  - `postUpdate(<Item>, <Value>)`
  - `createTimer(now.plusSeconds(n)) [ | ... ]`
  - `logInfo("tag", "message")`




