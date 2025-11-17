## Architecture Diagram

The diagram below illustrates the natural language to openHAB rule generation flow and the optional MCP server integration, focusing on the main components you interact with.

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#e3f2fd','primaryTextColor':'#000','primaryBorderColor':'#1976d2','lineColor':'#424242','secondaryColor':'#fff3e0','secondaryTextColor':'#000','secondaryBorderColor':'#f57c00','tertiaryColor':'#f3e5f5','tertiaryTextColor':'#000','tertiaryBorderColor':'#7b1fa2','background':'#ffffff','mainBkg':'#ffffff','nodeBorder':'#333','clusterBkg':'#fafafa','clusterBorder':'#999','edgeLabelBackground':'#ffffff'}}}%%
flowchart TD
  %% High-level architecture: OpenHAB Python agents + openHAB + optional MCP server

  subgraph A["OpenHAB Python Agents CLI"]
    U["1. Natural language rule<br/>User via CLI"] --> M["2. main.py<br/>CLI entrypoint"]
    M --> PG["5. PolicyGeneratorAgent<br/>agents/policy_generator.py"]
    M --> SV["6. ValidatorAgent<br/>Syntax validation<br/>agents/validator_agent.py"]
    M --> CV["7. ContextValidatorAgent<br/>Context-aware validation<br/>agents/context_validator.py"]
  end

  subgraph B["Context and System State"]
    CL["3. Context Loader<br/>tools/context_loader.py"]
    DOCS["Markdown docs<br/>context/*.md"]
    R["BM25 Retriever"]
    CF["4. SystemContextFetcher<br/>tools/context_fetcher.py"]
    OH["openHAB Server<br/>REST API"]
    GR["8. Generated openHAB rules<br/>generated_rules/*.rules"]
  end

  subgraph C["MCP Server Optional"]
    IDE["Claude / Cursor"]
    MCP["openHAB MCP Server<br/>openhab-mcp/openhab_mcp_server.py"]
  end

  %% Data flow: request → context → generation → validation → rules
  M -->|"load docs and build retriever"| CL
  CL --> DOCS
  CL --> R

  M -->|"fetch system context"| CF
  CF --> OH
  CF --> GR

  R -->|"relevant snippets"| PG
  PG -->|"rule candidates"| M
  M -->|"syntax validation first"| SV
  SV -->|"if syntax valid"| CV
  CV -->|"save approved rules"| GR

  %% MCP integration path (separate from Python agents)
  IDE --> MCP
  MCP --> OH

  %% Styling
  classDef inputNode fill:#4caf50,stroke:#2e7d32,stroke-width:3px,color:#fff
  classDef processNode fill:#2196f3,stroke:#1565c0,stroke-width:2px,color:#fff
  classDef dataNode fill:#ff9800,stroke:#e65100,stroke-width:2px,color:#fff
  classDef outputNode fill:#9c27b0,stroke:#6a1b9a,stroke-width:3px,color:#fff
  classDef mcpNode fill:#607d8b,stroke:#37474f,stroke-width:2px,color:#fff

  class U inputNode
  class M,PG,CV,SV,CL,CF processNode
  class DOCS,R,OH dataNode
  class GR outputNode
  class IDE,MCP mcpNode
```


