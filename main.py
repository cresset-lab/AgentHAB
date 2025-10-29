import os
import sys
import argparse
from dotenv import load_dotenv

from tools.context_loader import load_contexts
from agents.policy_generator import generate_openhab_code
from agents.validator_agent import validate_openhab_code
from tools.loader import save_rule


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="iconpal-openhab: NL -> openHAB code")
    parser.add_argument("prompt", type=str, nargs="*", help="Natural language request")
    parser.add_argument("--out", dest="out", type=str, default=None, help="Output filename .rules")
    args = parser.parse_args()

    if not args.prompt:
        print("Please provide a natural language request.")
        sys.exit(1)

    request = " ".join(args.prompt)

    retriever = load_contexts(path="./context", vs_path="./vectorstore/faiss")
    result = generate_openhab_code(request, retriever)

    is_valid, message = validate_openhab_code(result.openhab_code)
    if not is_valid:
        print("Validator warning:")
        print(message)

    path = save_rule(result.openhab_code, filename=args.out or "generated.rules")
    print(f"Saved rule to {path}")


if __name__ == "__main__":
    main()


