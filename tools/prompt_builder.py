from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

from langchain_core.documents import Document


@dataclass
class FeedbackEntry:
    source: str
    message: str


@dataclass
class PromptBuilder:
    """Collects retrieval context and validator feedback to construct prompts."""

    request: str
    documents: List[Document] = field(default_factory=list)
    feedback_history: List[FeedbackEntry] = field(default_factory=list)

    def add_feedback(self, source: str, message: str) -> None:
        """Persist feedback for subsequent regeneration attempts."""
        normalized = (message or "").strip()
        if not normalized:
            return
        self.feedback_history.append(FeedbackEntry(source=source, message=normalized))

    def generator_variables(self) -> dict:
        """Variables passed to the policy generator agent."""
        return {
            "request": self.request.strip(),
            "context": self._format_documents(),
            "feedback": self._format_feedback(),
        }

    def validator_variables(self, candidate_code: str) -> dict:
        """Variables passed to the validator agent."""
        base = self.generator_variables()
        base["candidate_code"] = candidate_code.strip()
        return base

    def _format_documents(self) -> str:
        if not self.documents:
            return "No supplemental documentation retrieved."
        blocks: List[str] = []
        for idx, doc in enumerate(self.documents, start=1):
            metadata = doc.metadata or {}
            source = metadata.get("source")
            label = f"[{idx}]"
            if source:
                label = f"{label} {os.path.basename(str(source))}"
            blocks.append(f"{label}\n{doc.page_content.strip()}")
        return "\n\n".join(blocks)

    def _format_feedback(self) -> str:
        if not self.feedback_history:
            return "None."
        lines = []
        for idx, entry in enumerate(self.feedback_history, start=1):
            lines.append(f"{idx}. ({entry.source}) {entry.message}")
        return "\n".join(lines)


