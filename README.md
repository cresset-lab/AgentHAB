# openHABAgents

An AI-powered tool that converts natural language automation requests into valid openHAB DSL rules and scripts. This project leverages LLMs to generate, validate, and deploy openHAB automation code without manual scripting.

## 🎯 Overview

openHABAgents provides two main components:

1. **Natural Language to openHAB Code Generator**: Convert plain English descriptions into openHAB rules using AI agents
2. **openHAB MCP Server**: A Model Context Protocol (MCP) server for AI assistants to interact with openHAB instances

## ✨ Features

- 🤖 **AI-Powered Code Generation**: Automatically generate openHAB rules from natural language
- ✅ **Built-in Validation**: LLM-based validator checks syntax and completeness
- 📚 **Context-Aware**: Uses RAG (Retrieval Augmented Generation) with openHAB documentation
- 🔧 **MCP Integration**: Connect Claude Desktop or Cline to your openHAB instance
- 💾 **Automatic Rule Saving**: Generated rules are saved to `generated_rules/` directory

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- OpenAI API key
- (Optional) Running openHAB instance for MCP server

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd openHABAgents
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### Basic Usage

Generate an openHAB rule from natural language:

```bash
python main.py "Turn on the living room light when motion is detected"
```

With custom output filename:

```bash
python main.py "Turn off all lights at midnight" --out nighttime.rules
```

## 📁 Project Structure

```
openHABAgents/
├── agents/
│   ├── policy_generator.py    # AI agent for code generation
│   └── validator_agent.py     # AI agent for code validation
├── context/
│   ├── examples_rules.md      # Example openHAB rules
│   ├── grammar_reference.md   # Syntax grammar reference
│   ├── openhab_syntax.md      # openHAB DSL syntax guide
│   └── tutorials.md           # Tutorial documentation
├── generated_rules/           # Output directory for generated rules
├── openhab-mcp-server/        # MCP server for AI assistant integration
├── tools/
│   ├── context_loader.py      # RAG context loading
│   ├── loader.py              # Rule file operations
│   └── openhab_api.py         # openHAB API utilities
├── vectorstore/               # FAISS vector store for RAG
├── main.py                    # Main CLI entry point
└── requirements.txt           # Python dependencies
```

## 🔧 How It Works

1. **Context Loading**: The system loads openHAB documentation, syntax guides, and examples into a vector store (FAISS)
2. **Retrieval**: When you provide a natural language request, relevant documentation is retrieved using BM25/semantic search
3. **Generation**: The policy generator agent uses GPT-4o-mini to create openHAB code based on your request and retrieved context
4. **Validation**: The validator agent checks the generated code for syntax issues, missing triggers, and other problems
5. **Saving**: Valid code is saved to the `generated_rules/` directory

## 🎯 Example Workflows

### Example 1: Motion-Activated Light
```bash
python main.py "When motion sensor in hallway triggers, turn on hallway light for 5 minutes"
```

### Example 2: Temperature Control
```bash
python main.py "If bedroom temperature is above 25°C, turn on the AC" --out bedroom_climate.rules
```

### Example 3: Time-Based Automation
```bash
python main.py "Every weekday at 7 AM, open the bedroom blinds and turn on the coffee maker"
```

## 🔌 openHAB MCP Server

The included MCP server allows AI assistants like Claude Desktop and Cline to interact with your openHAB instance.

### Features

- **Item Management**: List, create, update, delete items and states
- **Thing Management**: Full CRUD operations on things
- **Rule Management**: Create, update, run, and delete rules
- **Script Management**: Manage openHAB scripts
- **Link Management**: Handle item-channel links

### Quick Start with MCP Server

1. Navigate to the MCP server directory:
```bash
cd openhab-mcp-server
```

2. Run with Docker/Podman:
```bash
docker run -d --rm -p 8081:8080 \
  -e OPENHAB_URL=http://your-openhab-host:8080 \
  -e OPENHAB_API_TOKEN=your-api-token \
  --name openhab-mcp \
  ghcr.io/tdeckers/openhab-mcp:latest
```

For detailed MCP server setup, see [openhab-mcp-server/README.md](openhab-mcp-server/README.md).

## 📚 Adding Custom Context

To improve code generation for your specific setup:

1. Add example rules to `context/examples_rules.md`
2. Add custom syntax documentation to `context/openhab_syntax.md`
3. Delete the `vectorstore/` directory to rebuild the index
4. Run the tool again to regenerate the vector store

## 🛠️ Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENHAB_URL`: openHAB instance URL (for MCP server)
- `OPENHAB_API_TOKEN`: openHAB API token (for MCP server)
- `OPENHAB_USERNAME`: Basic auth username (optional)
- `OPENHAB_PASSWORD`: Basic auth password (optional)

### Command Line Arguments

```bash
python main.py [OPTIONS] <natural_language_request>

Options:
  --out FILENAME    Output filename (default: generated.rules)
```

## 🤝 Integration with openHAB

To use generated rules in your openHAB instance:

1. Copy the generated `.rules` file from `generated_rules/` to your openHAB `rules/` directory
2. openHAB will automatically detect and load the new rule
3. Monitor openHAB logs for any runtime errors

## 🧪 Development

### Project Dependencies

- `langchain>=0.2.14`: RAG framework
- `openai>=1.54.0`: OpenAI API client
- `python-dotenv>=1.0.1`: Environment variable management
- `requests>=2.32.3`: HTTP requests
- `rank-bm25>=0.2.2`: BM25 retrieval

### Agent Architecture

**Policy Generator Agent** (`agents/policy_generator.py`):
- Takes natural language input
- Retrieves relevant context from vector store
- Generates openHAB DSL code using GPT-4o-mini

**Validator Agent** (`agents/validator_agent.py`):
- Checks generated code for syntax errors
- Validates triggers, conditions, and actions
- Provides feedback on potential issues

## 📝 License

MIT

## 🙏 Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain)
- openHAB MCP server inspired by the Model Context Protocol
- Powered by OpenAI's GPT models

## 📮 Support

For issues and questions:
- Check existing rules in `generated_rules/` for examples
- Review context documentation in `context/`
- Consult the [openHAB documentation](https://www.openhab.org/docs/)

## 🚧 Future Enhancements

- [ ] Support for more openHAB scripting languages (JavaScript, Jython)
- [ ] Direct deployment to openHAB instance via REST API
- [ ] Interactive refinement of generated rules
- [ ] Rule testing and simulation
- [ ] Integration with openHAB's UI for item/thing discovery
- [ ] Multi-rule generation from complex scenarios

