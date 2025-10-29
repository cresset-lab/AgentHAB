from typing import List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import OpenAI


@dataclass
class GenerationResult:
    openhab_code: str
    reasoning: Optional[str] = None


SYSTEM_PROMPT = (
    "You are an expert openHAB policy/rules engineer. Given a natural language "
    "automation request and retrieved context (syntax, grammar, examples), "
    "produce valid openHAB code (DSL rules or JS Scripting) only. Use concise, "
    "idiomatic constructs and include triggers, conditions, and actions."
)


def _format_docs(docs: List) -> str:
    return "\n\n".join(getattr(d, "page_content", str(d)) for d in docs)


def generate_openhab_code(natural_language_request: str, retriever) -> GenerationResult:
    load_dotenv()
    # Retrieve context using the provided retriever (BM25 or similar)
    docs = retriever.invoke(natural_language_request)
    context = _format_docs(docs)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + "\n\nContext:\n" + context,
        },
        {
            "role": "user",
            "content": "Request: "
            + natural_language_request
            + "\n\nConstraints: Output openHAB code only.",
        },
    ]

    client = OpenAI()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
    )
    code = resp.choices[0].message.content or ""
    return GenerationResult(openhab_code=code)


