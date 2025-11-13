from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List, Optional

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI


@dataclass
class ValidationResult:
    verdict: str
    summary: str
    feedback: str
    fixes: List[str]
    raw_output: str

    @property
    def is_valid(self) -> bool:
        return self.verdict.lower().startswith("valid")

    def as_feedback_entry(self) -> str:
        if self.is_valid:
            return self.summary
        lines = [self.summary]
        if self.feedback:
            lines.append(self.feedback)
        if self.fixes:
            lines.extend(self.fixes)
        return "\n".join(lines)


class ValidatorAgent:
    """LangChain agent responsible for validating generated openHAB rules."""

    SYSTEM_PROMPT = (
        "You are an openHAB code validator. Given a user request, supporting context, "
        "and the candidate openHAB DSL code, determine whether the code is ready. "
        "Focus on syntax, missing triggers/actions, undefined items, and glaring logic issues. "
        "Respond strictly as a JSON object with keys: "
        "'verdict' ('valid' or 'invalid'), 'summary' (short sentence), "
        "'feedback' (string, may be empty), and optional 'fixes' (array of strings). "
        "Do not include markdown, code fences, or additional commentary."
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
                ("system", self.SYSTEM_PROMPT + "\nPrior validator feedback:\n{feedback}"),
                (
                    "user",
                    "User request:\n{request}\n\nContext snippets:\n{context}\n\n"
                    "Candidate openHAB code:\n{candidate_code}",
                ),
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

    def validate(
        self,
        *,
        request: str,
        context: str,
        feedback: str,
        candidate_code: str,
    ) -> ValidationResult:
        inputs = {
            "input": candidate_code,
            "request": request,
            "context": context,
            "feedback": feedback,
            "candidate_code": candidate_code,
        }
        result = self.executor.invoke(inputs)
        output = (result.get("output") or "").strip()
        parsed = self._parse_output(output)
        return ValidationResult(
            verdict=parsed.get("verdict", "invalid"),
            summary=parsed.get("summary", "Validator could not parse response."),
            feedback=parsed.get("feedback", ""),
            fixes=parsed.get("fixes", []),
            raw_output=output,
        )

    @staticmethod
    def _parse_output(output: str) -> dict:
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            sanitized = output.strip().strip("`")
            try:
                return json.loads(sanitized)
            except json.JSONDecodeError:
                return {
                    "verdict": "invalid",
                    "summary": "Unable to decode validator response.",
                    "feedback": sanitized,
                    "fixes": [],
                }

