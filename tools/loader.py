import os
from pathlib import Path


def save_rule(code: str, rules_dir: str | None = None, filename: str | None = None) -> str:
    """Write openHAB rule code to a .rules file in given directory.

    Returns path to the saved file.
    """
    base_dir = rules_dir or os.environ.get("OPENHAB_RULES_DIR", "./generated_rules")
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    fname = filename or "generated.rules"
    path = os.path.join(base_dir, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code.strip() + "\n")
    return path






