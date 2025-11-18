from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

# Ensure the project root (where `main.py` lives) is importable when this file
# is executed as a script (e.g., `python3 agent_pipeline/run_initial_pipeline.py`).
try:  # pragma: no cover - import path shim
    from main import run_generation_loop
except ModuleNotFoundError:  # pragma: no cover - defensive path handling
    ROOT_DIR = Path(__file__).resolve().parent.parent
    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))
    from main import run_generation_loop
from tools.context_loader import load_contexts
from tools.context_fetcher import SystemContextFetcher, SystemContext


DATASET_PATH = Path("datasets") / "intial_dataset.json"
# Store agent pipeline results under generated_rules/results to keep all
# experiment artefacts in a single tree alongside the baselines.
RESULTS_DIR = (
    Path("generated_rules") / "results" / "agents_workflow" / "initial"
)


def fetch_system_context() -> SystemContext | None:
    """
    Optionally fetch live system context via the MCP server, mirroring main.py.

    Controlled by the ENABLE_CONTEXT_VALIDATION environment variable.
    """
    enable_context = os.environ.get("ENABLE_CONTEXT_VALIDATION", "true").lower() != "false"
    if not enable_context:
        print("Context validation disabled via ENABLE_CONTEXT_VALIDATION.")
        return None

    print("\n=== Fetching live system context via MCP server (agent pipeline) ===")
    try:
        fetcher = SystemContextFetcher()
        context = fetcher.fetch_all()
        print("✓ System context loaded successfully\n")
        return context
    except Exception as exc:  # pragma: no cover - defensive logging
        print(f"⚠ Warning: Could not fetch system context: {exc}")
        print("Proceeding without context-aware validation.\n")
        return None


def load_dataset(path: Path) -> List[Dict[str, Any]]:
    """Load the initial dataset (id, text) pairs."""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected list at top level in {path}, got {type(data)}")
    return data


def run_agent_pipeline_on_initial_dataset(only_id: int | None = None) -> None:
    """
    Run the full agent pipeline on the initial dataset.

    For each example in datasets/intial_dataset.json (or a single example if
    `only_id` is provided), this will:
      - run the generation/validation loop (with optional context validation),
      - write the final openHAB DSL code to results/agents_workflow/initial/<id>.rules,
      - store a JSON summary of all runs in results/agents_workflow/initial/summary.json.
    """
    print(f"Loading initial dataset from {DATASET_PATH} ...")
    examples = load_dataset(DATASET_PATH)

    load_dotenv()
    retriever = load_contexts(path="./context", vs_path="./vectorstore/faiss")
    system_context = fetch_system_context()

    max_attempts = int(os.environ.get("GENERATION_MAX_ATTEMPTS", "3"))

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = RESULTS_DIR / "summary.json"

    results: List[Dict[str, Any]] = []

    for example in examples:
        ex_id = example.get("id")
        if only_id is not None and ex_id != only_id:
            continue

        text = (example.get("text") or "").strip()

        print(f"\n=== Agent pipeline run for id={ex_id} ===")
        print(f"Request: {text}")

        generation, validation, is_valid, attempts_used = run_generation_loop(
            request=text,
            retriever=retriever,
            max_attempts=max_attempts,
            system_context=system_context,
        )

        # Save final code to a .rules file
        rules_path = RESULTS_DIR / f"{ex_id}.rules"
        with rules_path.open("w", encoding="utf-8") as rf:
            rf.write(generation.openhab_code)

        result_entry: Dict[str, Any] = {
            "id": ex_id,
            "request": text,
            "openhab_code": generation.openhab_code,
            "is_valid": is_valid,
            "validator_summary": validation.summary,
            "rules_path": str(rules_path),
            # How many attempts the generator/validator loop actually used
            # for this example (needed for RQ1 analysis).
            "attempts_used": attempts_used,
        }
        results.append(result_entry)

    with summary_path.open("w", encoding="utf-8") as sf:
        json.dump(results, sf, indent=2)

    print(f"\nWrote {len(results)} agent pipeline results to {RESULTS_DIR}")
    print(f"Summary JSON: {summary_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the full agent-based generation/validation pipeline on the "
            "initial dataset (or a single example by id)."
        )
    )
    parser.add_argument(
        "--id",
        type=int,
        dest="only_id",
        help="If provided, run the pipeline only for this dataset id.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_agent_pipeline_on_initial_dataset(only_id=args.only_id)


if __name__ == "__main__":
    main()


