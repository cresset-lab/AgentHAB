from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Tuple

from dotenv import load_dotenv

from agents.policy_generator import GenerationResult, PolicyGeneratorAgent
from agents.validator_agent import ValidationResult, ValidatorAgent
from tools.context_loader import load_contexts
from tools.loader import save_rule
from tools.mcp_client import deploy_rule_via_mcp
from tools.prompt_builder import PromptBuilder


def run_generation_loop(
    request: str,
    retriever,
    *,
    max_attempts: int,
) -> Tuple[GenerationResult, ValidationResult]:
    """Iteratively generate and validate openHAB code with a retry guard."""
    docs = retriever.invoke(request)
    prompt_builder = PromptBuilder(request=request, documents=list(docs))
    generator = PolicyGeneratorAgent()
    validator = ValidatorAgent()

    last_validation: ValidationResult | None = None
    for attempt in range(1, max_attempts + 1):
        print(f"\n=== Generation attempt {attempt}/{max_attempts} ===")
        generation = generator.generate(**prompt_builder.generator_variables())
        validation = validator.validate(**prompt_builder.validator_variables(generation.openhab_code))

        if validation.is_valid:
            print("Validator: PASS")
            return generation, validation

        last_validation = validation
        feedback_entry = validation.as_feedback_entry()
        prompt_builder.add_feedback(source=f"validator attempt {attempt}", message=feedback_entry)
        print("Validator: FAIL")
        print(feedback_entry)

    message = (
        last_validation.as_feedback_entry() if last_validation else "Unknown validator failure."
    )
    raise RuntimeError(
        f"Failed to produce valid openHAB code after {max_attempts} attempts.\nLast feedback:\n{message}"
    )


def maybe_deploy_via_mcp(rule_code: str, *, request: str, destination_name: str) -> None:
    """Attempt to push the validated rule to the configured MCP server."""
    mcp_url = os.environ.get("OPENHAB_MCP_URL")
    if not mcp_url:
        print("MCP deployment skipped (OPENHAB_MCP_URL not set).")
        return

    success, message = deploy_rule_via_mcp(
        rule_code,
        rule_name=destination_name,
        metadata={"request": request},
    )
    status = "succeeded" if success else "failed"
    print(f"MCP deployment {status}: {message}")


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="iconpal-openhab: NL -> openHAB code")
    parser.add_argument("prompt", type=str, nargs="*", help="Natural language request")
    parser.add_argument("--out", dest="out", type=str, default=None, help="Output filename .rules")
    parser.add_argument(
        "--max-attempts",
        dest="max_attempts",
        type=int,
        default=int(os.environ.get("GENERATION_MAX_ATTEMPTS", "3")),
        help="Maximum generator/validator iterations (default: 3 or GENERATION_MAX_ATTEMPTS).",
    )
    args = parser.parse_args()

    if not args.prompt:
        print("Please provide a natural language request.")
        sys.exit(1)

    request = " ".join(args.prompt).strip()
    retriever = load_contexts(path="./context", vs_path="./vectorstore/faiss")

    try:
        generation, validation = run_generation_loop(
            request,
            retriever,
            max_attempts=args.max_attempts,
        )
    except RuntimeError as exc:
        print(str(exc))
        sys.exit(1)

    output_filename = args.out or "generated.rules"
    path = save_rule(generation.openhab_code, filename=output_filename)
    print(f"Saved rule to {path}")
    print(f"Validator summary: {validation.summary}")

    destination_name = Path(output_filename).stem
    maybe_deploy_via_mcp(generation.openhab_code, request=request, destination_name=destination_name)


if __name__ == "__main__":
    main()

