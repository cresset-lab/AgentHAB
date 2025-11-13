from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


@dataclass
class GenerationResult:
    openhab_code: str
    reasoning: Optional[str] = None


class PolicyGeneratorAgent:
    """LangChain agent responsible for synthesising openHAB rules."""

    SYSTEM_PROMPT = (
        "You are an expert openHAB policy engineer creating DSL rules. "
        "Rely on the supplied context snippets summarising syntax, grammar, and examples. "
        "Incorporate prior validator feedback when present. Respond with openHAB code only."
    )

    def __init__(
        self,
        *,
        model: str = "gpt-4o-mini",
        temperature: float = 1.5,
        llm: ChatOpenAI | None = None,
    ) -> None:
        self.llm = llm or ChatOpenAI(model=model, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    self.SYSTEM_PROMPT
                    + "\n\nContext snippets:\n{context}\n\n"
                    "Outstanding feedback to resolve:\n{feedback}",
                ),
                ("user", "User request:\n{request}"),
            ]
        )

    def generate(self, *, request: str, context: str, feedback: str) -> GenerationResult:
        """Invoke the agent and return the generated openHAB code."""
        prompt_messages = self.prompt.invoke(
            {"request": request, "context": context, "feedback": feedback}
        )
        response = self.llm.invoke(prompt_messages)
        code = (response.content or "").strip()
        return GenerationResult(openhab_code=code, reasoning=None)
