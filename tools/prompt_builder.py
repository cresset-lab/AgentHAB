from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

from langchain_core.documents import Document

if TYPE_CHECKING:
    from tools.context_fetcher import SystemContext


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
    last_candidate: Optional[str] = None
    system_context: Optional["SystemContext"] = None

    def add_feedback(self, source: str, message: str) -> None:
        """Persist feedback for subsequent regeneration attempts."""
        normalized = (message or "").strip()
        if not normalized:
            return
        self.feedback_history.append(FeedbackEntry(source=source, message=normalized))
    
    def set_system_context(self, context: "SystemContext") -> None:
        """Store live system state for prompt inclusion."""
        self.system_context = context

    def generator_variables(self) -> dict:
        """Variables passed to the policy generator agent."""
        base_vars = {
            "request": self.request.strip(),
            "context": self._format_documents(),
            "feedback": self._format_feedback(),
            "prior_code": self._format_prior_code(),
        }
        
        # Add system context if available
        if self.system_context:
            base_vars["context"] = self._format_documents() + "\n\n" + self._format_system_context()
        
        return base_vars

    def validator_variables(self, candidate_code: str) -> dict:
        """Variables passed to the validator agent."""
        base = self.generator_variables()
        base.pop("prior_code", None)
        base["candidate_code"] = candidate_code.strip()
        return base

    def record_candidate(self, candidate_code: str) -> None:
        self.last_candidate = candidate_code.strip()

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

    def _format_prior_code(self) -> str:
        if not self.last_candidate:
            return "None. Produce a fresh, fully-specified rule."
        return self.last_candidate
    
    def _format_system_context(self) -> str:
        """Format live system context for generator prompt."""
        if not self.system_context:
            return ""
        
        lines = ["=== LIVE SYSTEM CONTEXT ==="]
        
        # Available items
        if self.system_context.items:
            lines.append(f"\nAvailable Items ({len(self.system_context.items)}):")
            # Show all item names grouped by type
            items_by_type = {}
            for item in self.system_context.items:
                item_type = item.type or "Unknown"
                if item_type not in items_by_type:
                    items_by_type[item_type] = []
                items_by_type[item_type].append(item.name)
            
            for item_type, names in sorted(items_by_type.items()):
                lines.append(f"  {item_type}: {', '.join(sorted(names))}")
        
        # Existing rules (to avoid conflicts)
        total_rules = len(self.system_context.live_rules) + len(self.system_context.local_rules)
        if total_rules > 0:
            lines.append(f"\nExisting Rules ({total_rules} total):")
            lines.append("  IMPORTANT: Your generated rule must not conflict with these existing rules.")
            
            # Show rule names
            all_names = self.system_context.all_rule_names
            if all_names:
                lines.append(f"  Rule names: {', '.join(all_names[:15])}")
                if len(all_names) > 15:
                    lines.append(f"  ... and {len(all_names) - 15} more")
        
        return "\n".join(lines)


