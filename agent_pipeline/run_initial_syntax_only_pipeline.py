from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_community.retrievers import BM25Retriever
from langchain_text_splitters import RecursiveCharacterTextSplitter

try:  # pragma: no cover - import path shim
    from main import run_generation_loop
except ModuleNotFoundError:  # pragma: no cover - defensive path handling
    ROOT_DIR = Path(__file__).resolve().parent.parent
    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))
    from main import run_generation_loop
from tools.context_fetcher import SystemContextFetcher, SystemContext


DATASET_PATH = Path("datasets") / "intial_dataset.json"
RESULTS_DIR = (
    Path("generated_rules") / "results" / "agents_workflow" / "syntax_only_context"
)
SYNTAX_MD_PATH = Path("context") / "openhab_syntax.md"


def fetch_system_context() -> SystemContext | None:
    """
    Optionally fetch live system context via the MCP server, mirroring main.py.

    Controlled by the ENABLE_CONTEXT_VALIDATION environment variable.
    """
    enable_context = os.environ.get("ENABLE_CONTEXT_VALIDATION", "true").lower() != "false"
    if not enable_context:
        print("Context validation disabled via ENABLE_CONTEXT_VALIDATION.")
        return None

    print("\n=== Fetching live system context via MCP server (syntax-only context run) ===")
    try:
        fetcher = SystemContextFetcher()
        context = fetcher.fetch_all()
        print("✓ System context loaded successfully\n")
        return context
    except Exception as exc:  # pragma: no cover - defensive logging
        print(f"⚠ Warning: Could not fetch system context: {exc}")
        print("Proceeding without context-aware validation.\n")
        return None


def build_syntax_only_retriever():
    """
    Build a BM25 retriever using only `context/openhab_syntax.md`.

    This leaves other context files untouched on disk but excludes them from
    retrieval for this experiment run.
    """
    if not SYNTAX_MD_PATH.exists():
        raise FileNotFoundError(f"Syntax context file not found: {SYNTAX_MD_PATH}")

    loader = TextLoader(str(SYNTAX_MD_PATH), encoding="utf-8")
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = splitter.split_documents(docs)
    retriever = BM25Retriever.from_documents(split_docs)
    retriever.k = 3
    return retriever


def load_dataset(path: Path) -> List[Dict[str, Any]]:
    """Load the initial dataset (id, text) pairs."""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected list at top level in {path}, got {type(data)}")
    return data


def run_agent_pipeline_syntax_only(only_id: int | None = None) -> None:
    """
    Run the full agent pipeline on the initial dataset using syntax-only context.

    Uses only `openhab_syntax.md` for retrieval (no examples, tutorials, etc.).

    For each example in datasets/intial_dataset.json (or a single example if
    `only_id` is provided), this will:
      - run the generation/validation loop (with optional context validation),
      - write the final openHAB DSL code to
        datasets/agents_workflow/syntax_only_context/<id>.rules,
      - store a JSON summary of all runs in
        datasets/agents_workflow/syntax_only_context/summary.json.
    """
    print(f"Loading initial dataset from {DATASET_PATH} ...")
    examples = load_dataset(DATASET_PATH)

    load_dotenv()
    retriever = build_syntax_only_retriever()
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

        print(f"\n=== Agent pipeline (syntax-only context) run for id={ex_id} ===")
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
            "attempts_used": attempts_used,
        }
        results.append(result_entry)

    with summary_path.open("w", encoding="utf-8") as sf:
        json.dump(results, sf, indent=2)

    print(f"\nWrote {len(results)} agent pipeline (syntax-only) results to {RESULTS_DIR}")
    print(f"Summary JSON: {summary_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the agent generation/validation pipeline on the initial dataset "
            "using only openhab_syntax.md as retrieval context."
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
    run_agent_pipeline_syntax_only(only_id=args.only_id)


if __name__ == "__main__":
    main()



