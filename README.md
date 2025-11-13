# openHABAgents

openHABAgents is an AI-driven toolkit that turns natural language automation requests into executable openHAB DSL rules. It couples an iterative generation and validation loop with optional deployment through an MCP server so you can move from intent to live automation quickly and safely.

## Overview

The repository bundles two primary deliverables:

1. `main.py` orchestrates retrieval-augmented rule generation, iterative validation, and file management for `.rules` artifacts.
2. `openhab-mcp-server/` implements a Model Context Protocol (MCP) server so assistants that speak MCP can inspect and update an openHAB installation.

## Key Features

- AI-assisted rule authoring powered by LangChain and the `gpt-4o-mini` chat model.
- Iterative validator loop that incorporates structured feedback until a rule passes quality checks or the retry budget is exhausted.
- Retrieval over curated documentation in `context/` using the LangChain BM25 retriever.
- Configurable output location via `OPENHAB_RULES_DIR` with sensible defaults (`generated_rules/`).
- Optional automatic deployment to an MCP server by setting `OPENHAB_MCP_URL` (plus token support).
- Extensible prompt building that records prior candidates and validator feedback for subsequent iterations.

## Quick Start

### Prerequisites

- Python 3.10+ (virtual environments recommended).
- An `OPENAI_API_KEY` with access to the `gpt-4o-mini` model family.
- (Optional) An openHAB instance and the MCP server if you want automatic deployment.

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd openHABAgents
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Provide credentials (for example via `.env`):
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### CLI Usage

Run a request and let the agents iterate up to the default three attempts:

```bash
python main.py "Turn on the living room light when motion is detected"
```

Customise output and retry budget:

```bash
python main.py "Turn off all lights at midnight" --out nighttime.rules --max-attempts 5
```

Successful runs write a `.rules` file to `generated_rules/` (or the folder pointed to by `OPENHAB_RULES_DIR`) and print a validator summary.

### Optional MCP Deployment

If you want validated rules pushed to an MCP endpoint automatically, set:

- `OPENHAB_MCP_URL`: base URL of your MCP server (for example `https://example.com/mcp`).
- `OPENHAB_MCP_TOKEN` or `OPENHAB_STAGING_TOKEN`: bearer token for authenticated calls (optional).

When these are present and the validator reports success, `main.py` will invoke `tools/mcp_client.deploy_rule_via_mcp` to submit the rule.

## Project Structure

```
openHABAgents/
├── ARCHITECTURE.md               # High-level system design notes
├── agents/
│   ├── policy_generator.py       # LangChain-based rule generator
│   └── validator_agent.py        # Structured validator with JSON verdicts
├── context/                      # Retrieval corpus (markdown sources)
│   ├── examples_rules.md
│   ├── grammar_reference.md
│   ├── openhab_syntax.md
│   └── tutorials.md
├── generated_rules/              # Default output directory (created on demand)
├── openhab-mcp-server/           # Standalone MCP server implementation
├── tools/
│   ├── context_loader.py         # Builds the BM25 retriever
│   ├── loader.py                 # File saver supporting OPENHAB_RULES_DIR overrides
│   ├── mcp_client.py             # Thin HTTP client for MCP deployment
│   ├── openhab_api.py            # Direct REST convenience wrapper
│   └── prompt_builder.py         # Aggregates context, feedback, and prior code
├── main.py                       # CLI entry point
├── requirements.txt              # Python dependency pinning
└── README.md
```

See `openhab-mcp-server/README.md` for server-specific usage, environment variables, and Docker workflows.

## How It Works

1. **Context retrieval**: `tools/context_loader.load_contexts` ingests markdown files from `context/`, splits them with LangChain, and exposes a BM25 retriever.
2. **Prompt assembly**: `PromptBuilder` collates the request, retrieved snippets, and accumulated validator feedback to provide consistent inputs to both agents.
3. **Generation**: `PolicyGeneratorAgent` invokes `gpt-4o-mini` to synthesise a candidate `.rules` file, optionally guided by prior attempts.
4. **Validation**: `ValidatorAgent` evaluates the candidate, returning a structured verdict and feedback that either ends the loop or triggers another attempt.
5. **Persistence**: The most recent candidate is saved to disk via `tools.loader.save_rule`, respecting `OPENHAB_RULES_DIR` and the `--out` flag.
6. **Deployment (optional)**: When validation succeeds and MCP variables are configured, `tools.mcp_client.deploy_rule_via_mcp` posts the rule to your server.

## Custom Context

Tailor the retrieval corpus to mirror your installation:

1. Add or edit markdown files in `context/` with device-specific examples, naming conventions, or policies.
2. Run `python main.py ...` again; the retriever rebuilds in-memory on each execution, so no extra steps are required.
3. Keep long documents concise and well-structured so BM25 can surface the right fragments.

## Configuration

- `OPENAI_API_KEY` (required): credentials for the LangChain OpenAI client.
- `GENERATION_MAX_ATTEMPTS` (optional): overrides the default retry budget (`3`).
- `OPENHAB_RULES_DIR` (optional): directory for generated `.rules` files.
- `OPENHAB_MCP_URL` (optional): base URL for MCP deployment.
- `OPENHAB_MCP_TOKEN` / `OPENHAB_STAGING_TOKEN` (optional): bearer token headers for MCP calls.
- Additional variables for the MCP server (`OPENHAB_URL`, `OPENHAB_API_TOKEN`, etc.) are documented in `openhab-mcp-server/README.md`.

Command-line summary:

```bash
python main.py [OPTIONS] "<natural language request>"

Options:
  --out FILENAME       Custom output file name (default: generated.rules)
  --max-attempts N     Maximum generator/validator iterations
```

## Using Generated Rules in openHAB

1. Copy the generated `.rules` file from `generated_rules/` (or your chosen directory) into the `rules/` folder of your openHAB installation.
2. openHAB will detect the new rule automatically; monitor the logs to confirm activation.
3. If you prefer hands-free deployment, configure the MCP server and let the CLI push validated rules for you.

## Development

- Core dependencies are pinned in `requirements.txt` (LangChain, OpenAI SDK, python-dotenv, requests, rank-bm25).
- The MCP server publishes its own `pyproject.toml` with Hatch/Black/Flake8 tooling for contributors.
- Refer to `ARCHITECTURE.md` for design rationale and extension points.

## License

MIT

## Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain).
- Inspired by the Model Context Protocol initiative.
- Powered by OpenAI models.

## Support

- Browse `generated_rules/` for reference outputs.
- Review the curated documentation in `context/`.
- Consult the official [openHAB documentation](https://www.openhab.org/docs/).

## Future Enhancements

- [ ] Support additional openHAB scripting languages (JavaScript, Jython).
- [ ] Direct REST deployment into openHAB without MCP intermediaries.
- [ ] Interactive refinement loops with user feedback.
- [ ] Rule simulation and testing utilities.
- [ ] Enhanced item/thing discovery from openHAB APIs.
- [ ] Multi-rule orchestration for complex automation scenarios.

