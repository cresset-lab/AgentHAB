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
) -> Tuple[GenerationResult, ValidationResult, bool]:
    """Iteratively generate and validate openHAB code with a retry guard."""
    docs = retriever.invoke(request)
    prompt_builder = PromptBuilder(request=request, documents=list(docs))
    generator = PolicyGeneratorAgent()
    validator = ValidatorAgent()

    last_validation: ValidationResult | None = None
    last_generation: GenerationResult | None = None
    for attempt in range(1, max_attempts + 1):
        print(f"\n=== Generation attempt {attempt}/{max_attempts} ===")
        generation = generator.generate(**prompt_builder.generator_variables())
        prompt_builder.record_candidate(generation.openhab_code)
        validation = validator.validate(**prompt_builder.validator_variables(generation.openhab_code))
        last_generation = generation

        if validation.is_valid:
            print("Validator: PASS")
            return generation, validation, True

        last_validation = validation
        feedback_entry = validation.as_feedback_entry()
        prompt_builder.add_feedback(source=f"validator attempt {attempt}", message=feedback_entry)
        print("Validator: FAIL")
        print(feedback_entry)

    if last_generation is None or last_validation is None:
        raise RuntimeError("Generation loop terminated without producing any attempts.")

    print(
        f"Exceeded {max_attempts} attempts without validator approval. "
        "Saving latest result for manual review."
    )
    return last_generation, last_validation, False


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

    generation, validation, is_valid = run_generation_loop(
        request,
        retriever,
        max_attempts=args.max_attempts,
    )

    output_filename = args.out or "generated.rules"
    path = save_rule(generation.openhab_code, filename=output_filename)
    print(f"Saved rule to {path}")
    print(f"Validator summary: {validation.summary}")
    if not is_valid:
        print(validation.as_feedback_entry())

    destination_name = Path(output_filename).stem
    if is_valid:
        maybe_deploy_via_mcp(generation.openhab_code, request=request, destination_name=destination_name)
    else:
        print("Skipping MCP deployment because validator did not approve the rule.")


if __name__ == "__main__":
    main()

