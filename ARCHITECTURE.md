## Architecture Diagram

The diagram below illustrates the natural language to openHAB rule generation flow and the optional MCP server integration, focusing on the main components you interact with.

```mermaid
flowchart TD
  %% High-level architecture: OpenHAB Python agents + openHAB + optional MCP server

  subgraph A["OpenHAB Python Agents (CLI)"]
    U["1. Natural language rule (User via CLI)"] --> M["2. main.py (CLI entrypoint)"]
    M --> PG["5. PolicyGeneratorAgent\n(agents/policy_generator.py)"]
    M --> CV["6. ContextValidatorAgent\n(agents/context_validator.py)"]
    M --> SV["7. ValidatorAgent\n(agents/validator_agent.py)"]
  end

  subgraph B["Context & System State"]
    CL["3. Context Loader\n(tools/context_loader.py)"]
    DOCS["Markdown docs\n(context/*.md)"]
    R["BM25 Retriever"]
    CF["4. SystemContextFetcher\n(tools/context_fetcher.py)"]
    OH["openHAB Server\n(REST API)"]
    GR["8. Generated openHAB rules\n(generated_rules/*.rules)"]
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


