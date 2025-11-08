"""
Parser module for TagGroup activation conditions

This module provides functionality to parse, validate, and evaluate
activation conditions for TagGroups in the DatasetClassifier application.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
import re


class ConditionType(Enum):
    """Types of conditions that can be checked"""
    COMPLETED = "completed"
    HAS_TAG = "has"
    HAS_ALL_TAGS = "has_all"
    COUNT = "count"


class Operator(Enum):
    """Logical operators for combining conditions"""
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class ComparisonOp(Enum):
    """Comparison operators for count-based conditions"""
    EQUAL = "="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="


@dataclass
class Condition:
    """Represents a single condition check"""
    group_name: str
    condition_type: ConditionType
    tags: Optional[List[str]] = None  # For has/has_all
    count: Optional[int] = None  # For count
    comparison: Optional[ComparisonOp] = None  # For count


@dataclass
class ConditionNode:
    """Tree node for condition expressions"""
    operator: Optional[Operator] = None
    condition: Optional[Condition] = None
    left: Optional['ConditionNode'] = None
    right: Optional['ConditionNode'] = None
    negate: bool = False


def tokenize(condition_string: str) -> List[str]:
    """
    Tokenize the condition string into operators, parentheses, and conditions

    Args:
        condition_string: The condition string to tokenize

    Returns:
        List of tokens

    Examples:
        >>> tokenize("Torso[completed] AND Legs[completed]")
        ['Torso[completed]', 'AND', 'Legs[completed]']
    """
    if not condition_string or not condition_string.strip():
        return []

    tokens = []
    i = 0
    condition_string = condition_string.strip()

    while i < len(condition_string):
        # Skip whitespace
        while i < len(condition_string) and condition_string[i].isspace():
            i += 1

        if i >= len(condition_string):
            break

        # Try to match operators and special characters
        token, advance = _match_operator_or_paren(condition_string, i)
        if token:
            tokens.append(token)
            i += advance
        else:
            # Must be a condition - read until we hit a bracket
            i = _extract_condition_token(condition_string, i, tokens)

    return tokens


def _match_operator_or_paren(condition_string: str, i: int) -> tuple:
    """
    Try to match an operator or parenthesis at position i.

    Args:
        condition_string: The full condition string
        i: Current position

    Returns:
        Tuple of (token, advance_count) or (None, 0) if no match
    """
    # Check for 3-character operators first
    if condition_string[i:i+3] == 'AND':
        return ('AND', 3)
    if condition_string[i:i+3] == 'NOT':
        return ('NOT', 3)

    # Check for 2-character operators
    if condition_string[i:i+2] == 'OR':
        return ('OR', 2)
    if condition_string[i:i+2] == '&&':
        return ('AND', 2)
    if condition_string[i:i+2] == '||':
        return ('OR', 2)

    # Check for single-character tokens
    if condition_string[i] == '!':
        return ('NOT', 1)
    if condition_string[i] == '(':
        return ('(', 1)
    if condition_string[i] == ')':
        return (')', 1)

    return (None, 0)


def _extract_condition_token(condition_string: str, start: int, tokens: List[str]) -> int:
    """
    Extract a condition token from the string starting at position start.

    Args:
        condition_string: The full condition string
        start: Starting position for extraction
        tokens: List to append the extracted token to

    Returns:
        New position after extraction

    Raises:
        ValueError: If condition format is invalid
    """
    i = start

    # Find the opening bracket
    while i < len(condition_string) and condition_string[i] != '[':
        i += 1

    if i >= len(condition_string):
        raise ValueError(f"Invalid condition format at position {start}")

    # Now find the closing bracket
    i += 1  # Skip the '['
    bracket_count = 1
    while i < len(condition_string) and bracket_count > 0:
        if condition_string[i] == '[':
            bracket_count += 1
        elif condition_string[i] == ']':
            bracket_count -= 1
        i += 1

    if bracket_count != 0:
        raise ValueError(f"Unmatched brackets in condition starting at position {start}")

    # Extract the token
    token = condition_string[start:i].strip()
    if token:
        tokens.append(token)

    return i


def parse_single_condition(condition_str: str) -> Condition:
    """
    Parse a single condition like "Torso[completed]" or "Features[has:tag1,tag2]"

    Args:
        condition_str: A single condition string

    Returns:
        Condition object

    Raises:
        ValueError: If the condition format is invalid
    """
    # Extract group name and bracket contents
    match = re.match(r'^([A-Za-z0-9_ ]+)\[([^\]]+)\]$', condition_str.strip())
    if not match:
        raise ValueError(f"Invalid condition format: {condition_str}")

    group_name = match.group(1).strip()
    bracket_content = match.group(2).strip()

    # Parse bracket content based on condition type
    if bracket_content == "completed":
        return Condition(
            group_name=group_name,
            condition_type=ConditionType.COMPLETED
        )

    elif bracket_content.startswith("has_all:"):
        tags = [t.strip() for t in bracket_content[8:].split(',')]
        return Condition(
            group_name=group_name,
            condition_type=ConditionType.HAS_ALL_TAGS,
            tags=tags
        )

    elif bracket_content.startswith("has:"):
        tags = [t.strip() for t in bracket_content[4:].split(',')]
        return Condition(
            group_name=group_name,
            condition_type=ConditionType.HAS_TAG,
            tags=tags
        )

    elif "count" in bracket_content:
        # Parse count condition with comparison operator
        # Format: count>=3, count=2, count<5, etc.
        count_match = re.match(r'count\s*([><=]+)\s*(\d+)', bracket_content)
        if not count_match:
            raise ValueError(f"Invalid count condition format: {bracket_content}")

        op_str = count_match.group(1)
        count_value = int(count_match.group(2))

        # Map operator string to enum
        op_map = {
            '=': ComparisonOp.EQUAL,
            '>': ComparisonOp.GREATER,
            '>=': ComparisonOp.GREATER_EQUAL,
            '<': ComparisonOp.LESS,
            '<=': ComparisonOp.LESS_EQUAL,
        }

        if op_str not in op_map:
            raise ValueError(f"Invalid comparison operator: {op_str}")

        return Condition(
            group_name=group_name,
            condition_type=ConditionType.COUNT,
            count=count_value,
            comparison=op_map[op_str]
        )

    else:
        raise ValueError(f"Unknown condition type: {bracket_content}")


def parse_condition(condition_string: str) -> Optional[ConditionNode]:
    """
    Parse the full condition string into a tree structure

    Args:
        condition_string: The full condition expression

    Returns:
        Root ConditionNode of the expression tree, or None if empty

    Raises:
        ValueError: If the expression has syntax errors
    """
    if not condition_string or not condition_string.strip():
        return None

    tokens = tokenize(condition_string)
    if not tokens:
        return None

    # Use recursive descent parser
    parser = ConditionParser(tokens)
    return parser.parse_expression()


class ConditionParser:
    """Recursive descent parser for condition expressions"""

    def __init__(self, tokens: List[str]):
        self.tokens = tokens
        self.pos = 0

    def current_token(self) -> Optional[str]:
        """Get current token without consuming it"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume_token(self) -> Optional[str]:
        """Consume and return current token"""
        token = self.current_token()
        if token is not None:
            self.pos += 1
        return token

    def parse_expression(self) -> ConditionNode:
        """Parse OR expression (lowest precedence)"""
        left = self.parse_and_expression()

        while self.current_token() == 'OR':
            self.consume_token()
            right = self.parse_and_expression()
            left = ConditionNode(operator=Operator.OR, left=left, right=right)

        return left

    def parse_and_expression(self) -> ConditionNode:
        """Parse AND expression (higher precedence than OR)"""
        left = self.parse_not_expression()

        while self.current_token() == 'AND':
            self.consume_token()
            right = self.parse_not_expression()
            left = ConditionNode(operator=Operator.AND, left=left, right=right)

        return left

    def parse_not_expression(self) -> ConditionNode:
        """Parse NOT expression (highest precedence)"""
        if self.current_token() == 'NOT':
            self.consume_token()
            operand = self.parse_primary()
            return ConditionNode(operator=Operator.NOT, left=operand)

        return self.parse_primary()

    def parse_primary(self) -> ConditionNode:
        """Parse primary expression (parentheses or condition)"""
        token = self.current_token()

        if token == '(':
            self.consume_token()
            expr = self.parse_expression()
            if self.current_token() != ')':
                raise ValueError("Missing closing parenthesis")
            self.consume_token()
            return expr

        # Must be a condition
        if token and '[' in token:
            self.consume_token()
            try:
                condition = parse_single_condition(token)
                return ConditionNode(condition=condition)
            except ValueError as e:
                raise ValueError(f"Invalid condition: {e}")

        raise ValueError(f"Unexpected token: {token}")


def validate_references(node: Optional[ConditionNode], current_group, all_groups: List) -> None:
    """
    Validate that:
    1. Referenced groups exist
    2. Referenced groups appear BEFORE the current group (order check)
    3. Referenced tags exist in their groups

    Args:
        node: The condition tree to validate
        current_group: The TagGroup that owns this condition
        all_groups: List of all TagGroups in the project

    Raises:
        ValueError: If validation fails
    """
    if node is None:
        return

    # Recursively validate children
    if node.left:
        validate_references(node.left, current_group, all_groups)
    if node.right:
        validate_references(node.right, current_group, all_groups)

    # Validate the condition at this node
    if node.condition:
        condition = node.condition

        # Find the referenced group
        ref_group = None
        for group in all_groups:
            if group.name == condition.group_name:
                ref_group = group
                break

        if ref_group is None:
            raise ValueError(f"Referenced group '{condition.group_name}' does not exist")

        # Check that referenced group comes before current group
        if ref_group.order >= current_group.order:
            raise ValueError(
                f"Referenced group '{condition.group_name}' must appear before "
                f"'{current_group.name}' in the tag group order"
            )

        # Validate tag references
        if condition.tags:
            for tag_name in condition.tags:
                tag_exists = any(tag.name == tag_name for tag in ref_group.tags)
                if not tag_exists:
                    raise ValueError(
                        f"Tag '{tag_name}' does not exist in group '{condition.group_name}'"
                    )


def evaluate_condition(node: Optional[ConditionNode], image_tags: List[int],
                      all_groups: List) -> bool:
    """
    Evaluate if a condition is met for the current image

    Args:
        node: The condition tree to evaluate
        image_tags: List of tag IDs currently applied to the image
        all_groups: All tag groups for context

    Returns:
        True if condition is met, False otherwise
    """
    if node is None:
        return True

    # Handle operators
    if node.operator == Operator.AND:
        left_result = evaluate_condition(node.left, image_tags, all_groups)
        right_result = evaluate_condition(node.right, image_tags, all_groups)
        return left_result and right_result

    elif node.operator == Operator.OR:
        left_result = evaluate_condition(node.left, image_tags, all_groups)
        right_result = evaluate_condition(node.right, image_tags, all_groups)
        return left_result or right_result

    elif node.operator == Operator.NOT:
        operand_result = evaluate_condition(node.left, image_tags, all_groups)
        return not operand_result

    # Evaluate single condition
    elif node.condition:
        return evaluate_single_condition(node.condition, image_tags, all_groups)

    return False


def evaluate_single_condition(condition: Condition, image_tags: List[int],
                              all_groups: List) -> bool:
    """
    Evaluate a single condition

    Args:
        condition: The condition to evaluate
        image_tags: List of tag IDs currently applied to the image
        all_groups: All tag groups for context

    Returns:
        True if condition is met, False otherwise
    """
    # Find the group
    group = None
    for g in all_groups:
        if g.name == condition.group_name:
            group = g
            break

    if group is None:
        return False

    # Get tags from this group that are in image_tags
    group_tag_ids = [t.id for t in group.tags]
    selected_tags = [tid for tid in image_tags if tid in group_tag_ids]

    # Dispatch to appropriate evaluation function
    if condition.condition_type == ConditionType.COMPLETED:
        return _evaluate_completed(selected_tags, group)
    elif condition.condition_type == ConditionType.HAS_TAG:
        return _evaluate_has_tag(condition.tags, group, image_tags)
    elif condition.condition_type == ConditionType.HAS_ALL_TAGS:
        return _evaluate_has_all_tags(condition.tags, group, image_tags)
    elif condition.condition_type == ConditionType.COUNT:
        return _evaluate_count(selected_tags, condition)

    return False


def _evaluate_completed(selected_tags: List[int], group) -> bool:
    """Check if group meets its min_tags requirement"""
    return len(selected_tags) >= group.min_tags


def _evaluate_has_tag(tag_names: List[str], group, image_tags: List[int]) -> bool:
    """Check if any of the specified tags are present"""
    for tag_name in tag_names:
        for tag in group.tags:
            if tag.name == tag_name and tag.id in image_tags:
                return True
    return False


def _evaluate_has_all_tags(tag_names: List[str], group, image_tags: List[int]) -> bool:
    """Check if all specified tags are present"""
    for tag_name in tag_names:
        found = False
        for tag in group.tags:
            if tag.name == tag_name and tag.id in image_tags:
                found = True
                break
        if not found:
            return False
    return True


def _evaluate_count(selected_tags: List[int], condition: Condition) -> bool:
    """Compare count of selected tags against condition"""
    count = len(selected_tags)

    comparison_map = {
        ComparisonOp.EQUAL: lambda c, v: c == v,
        ComparisonOp.GREATER: lambda c, v: c > v,
        ComparisonOp.GREATER_EQUAL: lambda c, v: c >= v,
        ComparisonOp.LESS: lambda c, v: c < v,
        ComparisonOp.LESS_EQUAL: lambda c, v: c <= v,
    }

    comparator = comparison_map.get(condition.comparison)
    return comparator(count, condition.count) if comparator else False


def condition_to_string(node: Optional[ConditionNode]) -> str:
    """
    Convert a condition tree back to a human-readable string

    Args:
        node: The condition tree

    Returns:
        String representation of the condition
    """
    if node is None:
        return ""

    if node.operator == Operator.AND:
        left_str = condition_to_string(node.left)
        right_str = condition_to_string(node.right)
        return f"({left_str} AND {right_str})"

    elif node.operator == Operator.OR:
        left_str = condition_to_string(node.left)
        right_str = condition_to_string(node.right)
        return f"({left_str} OR {right_str})"

    elif node.operator == Operator.NOT:
        operand_str = condition_to_string(node.left)
        return f"NOT {operand_str}"

    elif node.condition:
        cond = node.condition
        if cond.condition_type == ConditionType.COMPLETED:
            return f"{cond.group_name}[completed]"
        elif cond.condition_type == ConditionType.HAS_TAG:
            tags_str = ",".join(cond.tags)
            return f"{cond.group_name}[has:{tags_str}]"
        elif cond.condition_type == ConditionType.HAS_ALL_TAGS:
            tags_str = ",".join(cond.tags)
            return f"{cond.group_name}[has_all:{tags_str}]"
        elif cond.condition_type == ConditionType.COUNT:
            op_str = cond.comparison.value
            return f"{cond.group_name}[count{op_str}{cond.count}]"

    return ""
