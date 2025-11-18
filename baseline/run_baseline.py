from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

from agents.policy_generator import PolicyGeneratorAgent
from tools.prompt_builder import PromptBuilder


def load_dataset(path: Path) -> List[Dict[str, Any]]:
    """Load a simple JSON list dataset with `id` and `text` fields."""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected list at top level in {path}, got {type(data)}")
    return data


def run_baseline_on_dataset(
    dataset_path: Path,
    output_path: Path,
    *,
    model: str = "gpt-4o-mini",
    temperature: float = 1.5,
    rules_dir: Path | None = None,
) -> None:
    """
    Run a single-shot LLM baseline on the given dataset.

    For each entry with fields:
      { "id": <int>, "text": <str> }
    we invoke the PolicyGeneratorAgent exactly once, with:
      - no retrieved documentation (empty context)
      - no prior feedback
      - no prior code
    and store the raw generated openHAB DSL code.

    Side effects:
      - Writes a JSON summary of all results to `output_path`.
      - If `rules_dir` is provided, also writes one `.rules` file per example
        to that directory, named `<id>.rules`.
    """
    print(f"Loading dataset from {dataset_path} ...")
    examples = load_dataset(dataset_path)

    generator = PolicyGeneratorAgent(model=model, temperature=temperature)
    results: List[Dict[str, Any]] = []

    if rules_dir is not None:
        rules_dir.mkdir(parents=True, exist_ok=True)

    for example in examples:
        ex_id = example.get("id")
        text = example.get("text", "")
        if text is None:
            text = ""
        text = str(text).strip()

        print(f"\n=== Running baseline for id={ex_id} ===")
        print(f"Request: {text}")

        # LLM-only baseline: no documents, no feedback, no prior code
        prompt_builder = PromptBuilder(request=text, documents=[])
        gen_vars = prompt_builder.generator_variables()

        generation = generator.generate(
            request=gen_vars["request"],
            context=gen_vars["context"],
            feedback=gen_vars["feedback"],
            prior_code=gen_vars["prior_code"],
        )

        rule_path: str | None = None
        if rules_dir is not None and generation.openhab_code:
            rule_file = rules_dir / f"{ex_id}.rules"
            with rule_file.open("w", encoding="utf-8") as rf:
                rf.write(generation.openhab_code)
            rule_path = str(rule_file)

        result_entry: Dict[str, Any] = {
            "id": ex_id,
            "request": text,
            "openhab_code": generation.openhab_code,
            "model": model,
            "temperature": temperature,
            "rule_path": rule_path,
        }
        results.append(result_entry)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nWrote {len(results)} baseline results to {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run LLM-only baseline (no validation, no iteration) on a dataset of "
            "natural-language openHAB automation requests."
        )
    )
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Path to input dataset JSON (e.g. datasets/intial_dataset.json).",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=False,
        help=(
            "Path to write JSON results. If omitted, results are written to "
            "datasets/results/<dataset-stem>_baseline_results.json. "
            "Per-example .rules files are always written to "
            "datasets/results/<dataset-base>/<id>.rules, where <dataset-base> "
            "is the dataset filename stem with an optional '_dataset' suffix "
            "removed (e.g., intial_dataset -> results/intial/)."
        ),
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI chat model name (default: gpt-4o-mini).",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=1.5,
        help="Sampling temperature for the LLM (default: 1.5, matching main pipeline).",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    dataset_path = Path(args.dataset)
    results_root = Path("datasets") / "results"

    # JSON summary output
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = results_root / f"{dataset_path.stem}_baseline_results.json"

    # Directory for individual .rules files
    stem = dataset_path.stem
    base_name = stem[:-len("_dataset")] if stem.endswith("_dataset") else stem
    rules_dir = results_root / base_name

    run_baseline_on_dataset(
        dataset_path=dataset_path,
        output_path=output_path,
        model=args.model,
        temperature=args.temperature,
        rules_dir=rules_dir,
    )


if __name__ == "__main__":
    main()


