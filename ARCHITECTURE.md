## Architecture Diagram

The diagram below illustrates the natural language to openHAB code generation flow and the optional MCP server integration for controlling a live openHAB instance.

```mermaid
flowchart TD
  %% Natural language to openHAB code generation with retrieval feedback loop
  subgraph A["NL to openHAB Code Generation"]
    U["User (CLI)"] --> M["main.py"]
    M --> C["Context Loader<br/>tools/context_loader.py"]
    C -->|"load & split"| D[("context/*.md")]
    C -->|"BM25"| R["Retriever"]
    M -->|"fetch system state"| CF["Context Fetcher<br/>tools/context_fetcher.py"]
    CF -->|"REST API"| OH["openHAB Instance<br/>(items, things, rules)"]
    CF -->|"parse local"| LR[("generated_rules/*.rules")]
    CF -->|"system context"| M
    M -->|"assemble prompts"| PB["Prompt Builder<br/>+system context"]
    R -->|"top-k snippets"| PB
    PB -->|"generator prompt"| G["Policy Generator<br/>agents/policy_generator.py"]
    G -->|"call"| OA[("OpenAI API<br/>gpt-4o-mini")]
    OA -->|"rule draft"| M
    M -->|"submit draft"| CV["Context Validator<br/>agents/context_validator.py"]
    CV -->|"check items,<br/>conflicts,<br/>security"| CRES{"context valid?"}
    CRES -->|No| CFB["Context Feedback"]
    CFB -->|"update instructions"| M
    CRES -->|Yes| V["Syntax Validator<br/>agents/validator_agent.py"]
    PB -->|"validator prompt"| V
    V -->|"call"| OA
    OA -->|"syntax report"| V
    V -->|"validation result"| RES{"syntax valid?"}
    RES -->|Yes| S["Save Rule<br/>tools/loader.py"]
    S --> F[("generated_rules/*.rules")]
    RES -->|No| FB["Syntax Feedback"]
    FB -->|"update instructions"| M
    M -->|"retry?"| Guard{"attempts < limit?"}
    Guard -->|Yes| PB
    Guard -->|No| Abort["surface error to user"]
  end

  %% MCP integration to control a live openHAB
  subgraph B["MCP Integration (optional)"]
    S -->|"deploy request"| Srv["openhab-mcp-server/openhab_mcp_server.py"]
    Srv -->|"REST"| OHStg["openHAB Staging Instance"]
    OHStg -->|"runtime feedback"| Srv
    Srv -->|"issues / success"| M
  end

  %% Deploy rule into openHAB (manual or production)
  F -. "manual copy (fallback)" .-> OHProd["openHAB Production"]

  %% Environment variables
  classDef env fill:#eef,stroke:#99f,stroke-width:1px,color:#000
  E1[["OPENAI_API_KEY"]]:::env --> OA
  E2[["OPENHAB_URL<br/>OPENHAB_API_TOKEN"]]:::env --> Srv
  E3[["OPENHAB_STAGING_URL<br/>OPENHAB_STAGING_TOKEN"]]:::env --> Srv
```


