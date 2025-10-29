from typing import Tuple
from dotenv import load_dotenv
from openai import OpenAI


def validate_openhab_code(code: str) -> Tuple[bool, str]:
    """Lightweight LLM-based validator for openHAB rules syntax sanity.

    Returns (is_valid, message).
    """
    load_dotenv()
    system = (
        "You are an openHAB code validator. Check for obvious syntax issues, "
        "missing triggers, mis-typed keywords, and undefined items in code. "
        "Respond with either VALID or INVALID and a short reason."
    )
    messages = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": "Evaluate this openHAB code for syntactic correctness and completeness:\n" + code,
        },
    ]
    client = OpenAI()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
    )
    result = resp.choices[0].message.content or ""
    normalized = result.strip().upper()
    if normalized.startswith("VALID"):
        return True, result
    return False, result


