## Architecture Diagram

The diagram below illustrates the natural language to openHAB rule generation flow and the optional MCP server integration, focusing on the main components you interact with.

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#e3f2fd','primaryTextColor':'#000','primaryBorderColor':'#1976d2','lineColor':'#424242','secondaryColor':'#fff3e0','secondaryTextColor':'#000','secondaryBorderColor':'#f57c00','tertiaryColor':'#f3e5f5','tertiaryTextColor':'#000','tertiaryBorderColor':'#7b1fa2','background':'#ffffff','mainBkg':'#ffffff','nodeBorder':'#333','clusterBkg':'#fafafa','clusterBorder':'#999','edgeLabelBackground':'#ffffff'}}}%%
flowchart TD
  %% Complete rule generation and validation flow

  Start["1. User: Natural language<br/>automation request via CLI"] --> Main["2. main.py<br/>CLI entrypoint & orchestrator"]
  
  Main --> LoadContext["3. Load Context<br/>- Documentation (context/*.md)<br/>- BM25 Retriever"]
  LoadContext --> FetchSystem["4. Fetch System Context<br/>(optional, can be disabled)<br/>- Items, Things, Existing Rules<br/>via MCP Server"]
  
  FetchSystem --> GenLoop["5. Generation Loop<br/>(max_attempts)"]
  
  GenLoop --> Generate["6. PolicyGeneratorAgent<br/>Generate openHAB DSL rule<br/>using context + feedback"]
  
  Generate --> SyntaxVal["7. ValidatorAgent<br/>Syntax validation<br/>(structure, grammar, DSL)"]
  
  SyntaxVal -->|"❌ Syntax Invalid"| Feedback1["Add syntax errors<br/>to feedback"]
  Feedback1 --> CheckAttempts1{Reached<br/>max attempts?}
  CheckAttempts1 -->|"No"| Generate
  CheckAttempts1 -->|"Yes"| SaveRules
  
  SyntaxVal -->|"✅ Syntax Valid"| ContextCheck{Context validation<br/>enabled?}
  
  ContextCheck -->|"No (disabled via<br/>--no-context-validation)"| SaveRules["10. Save Rules<br/>generated_rules/*.rules<br/>(ALWAYS saves)"]
  
  ContextCheck -->|"Yes (default)"| ContextVal["8. ContextValidatorAgent<br/>Validate against live system<br/>(items exist, types match,<br/>no conflicts, security)"]
  
  ContextVal -->|"❌ Context Invalid"| Feedback2["Add context errors<br/>to feedback"]
  Feedback2 --> CheckAttempts2{Reached<br/>max attempts?}
  CheckAttempts2 -->|"No"| Generate
  CheckAttempts2 -->|"Yes"| SaveRules
  
  ContextVal -->|"✅ Valid (with<br/>optional warnings)"| SaveRules
  
  SaveRules --> DeployCheck{Rules fully<br/>valid &<br/>MCP configured?}
  
  DeployCheck -->|"Yes"| Deploy["11. Deploy to openHAB<br/>via MCP Server<br/>(optional)"]
  DeployCheck -->|"No"| End["12. Complete<br/>Rules saved locally<br/>for manual review"]
  Deploy --> End

  subgraph Context["Context Sources"]
    Docs["Documentation<br/>context/*.md"]
    SystemState["Live System State<br/>- Items<br/>- Things<br/>- Existing Rules"]
    OH["openHAB Instance<br/>(REST API)"]
  end

  subgraph MCP["MCP Server (Separate Tool)"]
    MCPServer["openhab-mcp-server<br/>Python MCP implementation"]
    IDE["Claude/Cursor<br/>Direct IDE integration"]
  end

  LoadContext -.->|"reads"| Docs
  FetchSystem -.->|"queries via"| MCPServer
  MCPServer -.->|"REST API"| OH
  Deploy -.->|"deploys via"| MCPServer
  IDE -.->|"uses"| MCPServer
  
  SystemState -.->|"retrieved from"| OH

  %% Styling
  classDef inputNode fill:#4caf50,stroke:#2e7d32,stroke-width:3px,color:#fff
  classDef processNode fill:#2196f3,stroke:#1565c0,stroke-width:2px,color:#fff
  classDef validationNode fill:#ff9800,stroke:#e65100,stroke-width:2px,color:#fff
  classDef decisionNode fill:#9c27b0,stroke:#6a1b9a,stroke-width:2px,color:#fff
  classDef outputNode fill:#4caf50,stroke:#2e7d32,stroke-width:3px,color:#fff
  classDef dataNode fill:#607d8b,stroke:#37474f,stroke-width:2px,color:#fff
  classDef loopNode fill:#f44336,stroke:#c62828,stroke-width:2px,color:#fff

  class Start inputNode
  class Main,LoadContext,FetchSystem,Generate,GenLoop processNode
  class SyntaxVal,ContextVal validationNode
  class ContextCheck,DeployCheck,CheckAttempts1,CheckAttempts2 decisionNode
  class SaveRules,Deploy,End outputNode
  class Docs,SystemState,OH,MCPServer,IDE dataNode
  class Feedback1,Feedback2 loopNode
```


