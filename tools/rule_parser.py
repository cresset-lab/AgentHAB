"""Simple DSL rule parser to extract structured information for validation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class ParsedRule:
    """Structured representation of a parsed openHAB DSL rule."""
    
    name: str
    raw_text: str
    trigger_items: List[str]  # Items referenced in when clause
    action_items: List[str]   # Items referenced in then clause
    all_items: List[str]      # All item references
    source_file: Optional[str] = None
    
    def __str__(self) -> str:
        return f"Rule '{self.name}' (triggers: {self.trigger_items}, actions: {self.action_items})"


class RuleParser:
    """Parse openHAB DSL rules to extract structure for validation."""
    
    # Regex patterns for rule parsing
    RULE_PATTERN = re.compile(r'rule\s+"([^"]+)"', re.IGNORECASE)
    WHEN_PATTERN = re.compile(r'\bwhen\b(.*?)\bthen\b', re.DOTALL | re.IGNORECASE)
    THEN_PATTERN = re.compile(r'\bthen\b(.*?)\bend\b', re.DOTALL | re.IGNORECASE)
    
    # Item reference patterns (e.g., My_Lamp, MotionSensor, Temperature_Sensor)
    ITEM_PATTERN = re.compile(r'\b([A-Z][A-Za-z0-9_]*)\b')
    
    # Specific item patterns in different contexts
    ITEM_CHANGED_PATTERN = re.compile(r'Item\s+(\w+)\s+(?:changed|received)', re.IGNORECASE)
    SEND_COMMAND_PATTERN = re.compile(r'sendCommand\s*\(\s*(\w+)', re.IGNORECASE)
    POST_UPDATE_PATTERN = re.compile(r'postUpdate\s*\(\s*(\w+)', re.IGNORECASE)
    ITEM_STATE_PATTERN = re.compile(r'(\w+)\.state', re.IGNORECASE)
    
    def parse_rule(self, rule_text: str, source_file: Optional[str] = None) -> Optional[ParsedRule]:
        """Extract structured information from a single rule."""
        rule_text = rule_text.strip()
        if not rule_text or 'rule' not in rule_text.lower():
            return None
        
        # Extract rule name
        name_match = self.RULE_PATTERN.search(rule_text)
        if not name_match:
            return None
        rule_name = name_match.group(1)
        
        # Extract when clause
        when_match = self.WHEN_PATTERN.search(rule_text)
        when_clause = when_match.group(1) if when_match else ""
        
        # Extract then clause
        then_match = self.THEN_PATTERN.search(rule_text)
        then_clause = then_match.group(1) if then_match else ""
        
        # Extract items from when clause (triggers)
        trigger_items = self._extract_items_from_when(when_clause)
        
        # Extract items from then clause (actions)
        action_items = self._extract_items_from_then(then_clause)
        
        # All unique items
        all_items = list(set(trigger_items + action_items))
        
        return ParsedRule(
            name=rule_name,
            raw_text=rule_text,
            trigger_items=trigger_items,
            action_items=action_items,
            all_items=all_items,
            source_file=source_file,
        )
    
    def _extract_items_from_when(self, when_clause: str) -> List[str]:
        """Extract item names from when clause."""
        items = []
        
        # Pattern: Item MyItem changed/received
        for match in self.ITEM_CHANGED_PATTERN.finditer(when_clause):
            items.append(match.group(1))
        
        # Also look for .state references
        for match in self.ITEM_STATE_PATTERN.finditer(when_clause):
            items.append(match.group(1))
        
        return list(set(items))
    
    def _extract_items_from_then(self, then_clause: str) -> List[str]:
        """Extract item names from then clause."""
        items = []
        
        # Pattern: sendCommand(MyItem, ...)
        for match in self.SEND_COMMAND_PATTERN.finditer(then_clause):
            items.append(match.group(1))
        
        # Pattern: postUpdate(MyItem, ...)
        for match in self.POST_UPDATE_PATTERN.finditer(then_clause):
            items.append(match.group(1))
        
        # Pattern: MyItem.state
        for match in self.ITEM_STATE_PATTERN.finditer(then_clause):
            items.append(match.group(1))
        
        return list(set(items))
    
    def extract_item_references(self, rule_text: str) -> List[str]:
        """Extract all item references from rule text."""
        parsed = self.parse_rule(rule_text)
        return parsed.all_items if parsed else []
    
    def parse_rules_file(self, file_path: Path) -> List[ParsedRule]:
        """Parse all rules from a .rules file."""
        if not file_path.exists():
            return []
        
        content = file_path.read_text(encoding='utf-8')
        return self.parse_rules_text(content, str(file_path))
    
    def parse_rules_text(self, content: str, source_file: Optional[str] = None) -> List[ParsedRule]:
        """Parse multiple rules from text content."""
        # Split by 'rule' keyword but keep it
        rule_blocks = re.split(r'(?=\brule\s+")', content, flags=re.IGNORECASE)
        
        parsed_rules = []
        for block in rule_blocks:
            if not block.strip():
                continue
            
            # Remove markdown code fences if present
            clean_block = re.sub(r'^```.*$', '', block, flags=re.MULTILINE)
            clean_block = clean_block.strip()
            
            parsed = self.parse_rule(clean_block, source_file)
            if parsed:
                parsed_rules.append(parsed)
        
        return parsed_rules

