## Architecture Diagram

The diagram below illustrates the natural language to openHAB rule generation flow and the optional MCP server integration, focusing on the main components you interact with.

```mermaid
flowchart TD
  %% High-level architecture: Python agents + openHAB + optional MCP server

  subgraph A["Python Agents (CLI)"]
    U["User (CLI)"] --> M["main.py"]
    M --> PG["PolicyGeneratorAgent\n(agents/policy_generator.py)"]
    M --> CV["ContextValidatorAgent\n(agents/context_validator.py)"]
    M --> SV["ValidatorAgent\n(agents/validator_agent.py)"]
  end

  subgraph B["Context & System State"]
    CL["Context Loader\n(tools/context_loader.py)"]
    DOCS["Markdown docs\n(context/*.md)"]
    R["BM25 Retriever"]
    CF["SystemContextFetcher\n(tools/context_fetcher.py)"]
    OH["openHAB Server\n(REST API)"]
    GR["Generated rules\n(generated_rules/*.rules)"]
  end

  subgraph C["MCP Server (optional)"]
    IDE["Claude / Cursor"]
    MCP["openHAB MCP Server\n(openhab-mcp/openhab_mcp_server.py)"]
  end

  %% Data flow: request → context → generation → validation → rules
  M -->|"load docs & build retriever"| CL
  CL --> DOCS
  CL --> R

  M -->|"fetch system context"| CF
  CF --> OH
  CF --> GR

  R -->|"relevant snippets"| PG
  PG -->|"rule candidates"| M
  M -->|"context-aware checks"| CV
  M -->|"syntax validation"| SV
  SV -->|"save approved rules"| GR

  %% MCP integration path (separate from Python agents)
  IDE --> MCP
  MCP --> OH
```


