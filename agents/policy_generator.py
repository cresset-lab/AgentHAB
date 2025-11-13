from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
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
        temperature: float = 0.0,
        llm: ChatOpenAI | None = None,
    ) -> None:
        self.llm = llm or ChatOpenAI(model=model, temperature=temperature)
        self.tools = []
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    self.SYSTEM_PROMPT
                    + "\n\nContext snippets:\n{context}\n\n"
                    "Outstanding feedback to resolve:\n{feedback}",
                ),
                ("user", "User request:\n{request}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=False,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
        )

    def generate(self, *, request: str, context: str, feedback: str) -> GenerationResult:
        """Invoke the agent and return the generated openHAB code."""
        inputs = {"input": request, "request": request, "context": context, "feedback": feedback}
        result = self.executor.invoke(inputs)
        code = (result.get("output") or "").strip()
        reasoning = None
        if intermediate := result.get("intermediate_steps"):
            reasoning = repr(intermediate)
        return GenerationResult(openhab_code=code, reasoning=reasoning)
