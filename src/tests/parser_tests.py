"""
Unit tests for the condition parser

Run with: python -m pytest test_parser.py -v
"""

import pytest
from src.parser import (
    parse_condition, 
    evaluate_condition, 
    validate_references,
    tokenize,
    parse_single_condition,
    ConditionType,
    ComparisonOp
)


# Mock TagGroup and Tag classes for testing
class MockTag:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class MockTagGroup:
    def __init__(self, id, name, order, min_tags=1, tags=None):
        self.id = id
        self.name = name
        self.order = order
        self.min_tags = min_tags
        self.tags = tags or []
        self.condition = None


class TestTokenization:
    """Test the tokenization function"""
    
    def test_simple_condition(self):
        result = tokenize("Torso[completed]")
        assert result == ["Torso[completed]"]
    
    def test_and_operator(self):
        result = tokenize("Torso[completed] AND Legs[completed]")
        assert result == ["Torso[completed]", "AND", "Legs[completed]"]
    
    def test_or_operator(self):
        result = tokenize("Torso[completed] OR Legs[completed]")
        assert result == ["Torso[completed]", "OR", "Legs[completed]"]
    
    def test_not_operator(self):
        result = tokenize("NOT Torso[completed]")
        assert result == ["NOT", "Torso[completed]"]
    
    def test_parentheses(self):
        result = tokenize("(Torso[completed] AND Legs[completed])")
        assert result == ["(", "Torso[completed]", "AND", "Legs[completed]", ")"]
    
    def test_complex_expression(self):
        result = tokenize("(Torso[completed] OR Legs[completed]) AND Features[count>=2]")
        assert "(" in result
        assert ")" in result
        assert "AND" in result
        assert "OR" in result
    
    def test_alternative_operators(self):
        result = tokenize("Torso[completed] && Legs[completed]")
        assert result == ["Torso[completed]", "AND", "Legs[completed]"]
        
        result = tokenize("Torso[completed] || Legs[completed]")
        assert result == ["Torso[completed]", "OR", "Legs[completed]"]
        
        result = tokenize("! Torso[completed]")
        assert result == ["NOT", "Torso[completed]"]


class TestSingleConditionParsing:
    """Test parsing of individual conditions"""
    
    def test_completed_condition(self):
        condition = parse_single_condition("Torso[completed]")
        assert condition.group_name == "Torso"
        assert condition.condition_type == ConditionType.COMPLETED
    
    def test_has_condition(self):
        condition = parse_single_condition("Torso[has:fur-covered torso]")
        assert condition.group_name == "Torso"
        assert condition.condition_type == ConditionType.HAS_TAG
        assert condition.tags == ["fur-covered torso"]
    
    def test_has_multiple_tags(self):
        condition = parse_single_condition("Torso[has:fur,scales,skin]")
        assert condition.tags == ["fur", "scales", "skin"]
    
    def test_has_all_condition(self):
        condition = parse_single_condition("Features[has_all:claws,fangs]")
        assert condition.condition_type == ConditionType.HAS_ALL_TAGS
        assert condition.tags == ["claws", "fangs"]
    
    def test_count_equal(self):
        condition = parse_single_condition("Body[count=2]")
        assert condition.condition_type == ConditionType.COUNT
        assert condition.count == 2
        assert condition.comparison == ComparisonOp.EQUAL
    
    def test_count_greater_equal(self):
        condition = parse_single_condition("Body[count>=3]")
        assert condition.condition_type == ConditionType.COUNT
        assert condition.count == 3
        assert condition.comparison == ComparisonOp.GREATER_EQUAL
    
    def test_count_less(self):
        condition = parse_single_condition("Body[count<5]")
        assert condition.comparison == ComparisonOp.LESS
        assert condition.count == 5
    
    def test_group_name_with_spaces(self):
        condition = parse_single_condition("Body Features[completed]")
        assert condition.group_name == "Body Features"
    
    def test_invalid_format_raises_error(self):
        with pytest.raises(ValueError):
            parse_single_condition("InvalidFormat")
        
        with pytest.raises(ValueError):
            parse_single_condition("Torso[unknown_condition]")


class TestConditionParsing:
    """Test parsing of full condition expressions"""
    
    def test_simple_condition(self):
        node = parse_condition("Torso[completed]")
        assert node is not None
        assert node.condition is not None
        assert node.condition.group_name == "Torso"
    
    def test_and_expression(self):
        node = parse_condition("Torso[completed] AND Legs[completed]")
        assert node is not None
        assert node.operator.value == "AND"
        assert node.left is not None
        assert node.right is not None
    
    def test_or_expression(self):
        node = parse_condition("Torso[completed] OR Legs[completed]")
        assert node.operator.value == "OR"
    
    def test_not_expression(self):
        node = parse_condition("NOT Torso[completed]")
        assert node.operator.value == "NOT"
        assert node.left is not None
    
    def test_parentheses(self):
        node = parse_condition("(Torso[completed] AND Legs[completed])")
        assert node.operator.value == "AND"
    
    def test_complex_expression(self):
        expr = "(Torso[completed] OR Legs[completed]) AND Features[count>=2]"
        node = parse_condition(expr)
        assert node is not None
        # Root should be AND
        assert node.operator.value == "AND"
        # Left should be OR in parentheses
        assert node.left.operator.value == "OR"
        # Right should be a count condition
        assert node.right.condition.condition_type == ConditionType.COUNT
    
    def test_operator_precedence(self):
        # AND has higher precedence than OR
        # A OR B AND C should parse as A OR (B AND C)
        node = parse_condition("A[completed] OR B[completed] AND C[completed]")
        assert node.operator.value == "OR"
        assert node.right.operator.value == "AND"
    
    def test_empty_condition(self):
        node = parse_condition("")
        assert node is None
        
        node = parse_condition("   ")
        assert node is None


class TestConditionEvaluation:
    """Test evaluation of conditions against image tags"""
    
    def setup_method(self):
        """Set up test data"""
        # Create mock groups
        self.torso_group = MockTagGroup(1, "Torso", 0, min_tags=1, tags=[
            MockTag(101, "fur-covered torso"),
            MockTag(102, "scale-covered torso"),
            MockTag(103, "normal torso"),
        ])
        
        self.legs_group = MockTagGroup(2, "Legs", 1, min_tags=1, tags=[
            MockTag(201, "fur-covered legs"),
            MockTag(202, "scale-covered legs"),
        ])
        
        self.features_group = MockTagGroup(3, "Features", 2, min_tags=2, tags=[
            MockTag(301, "claws"),
            MockTag(302, "fangs"),
            MockTag(303, "wings"),
        ])
        
        self.all_groups = [self.torso_group, self.legs_group, self.features_group]
    
    def test_completed_condition_true(self):
        # Torso group requires 1 tag, image has 1
        image_tags = [101]  # fur-covered torso
        node = parse_condition("Torso[completed]")
        result = evaluate_condition(node, image_tags, self.all_groups)
        assert result is True
    
    def test_completed_condition_false(self):
        # Features group requires 2 tags, image has 1
        image_tags = [301]  # only claws
        node = parse_condition("Features[completed]")
        result = evaluate_condition(node, image_tags, self.all_groups)
        assert result is False
    
    def test_has_condition_true(self):
        image_tags = [101]  # fur-covered torso
        node = parse_condition("Torso[has:fur-covered torso]")
        result = evaluate_condition(node, image_tags, self.all_groups)
        assert result is True
    
    def test_has_condition_false(self):
        image_tags = [102]  # scale-covered torso
        node = parse_condition("Torso[has:fur-covered torso]")
        result = evaluate_condition(node, image_tags, self.all_groups)
        assert result is False
    
    def test_has_multiple_tags_any(self):
        image_tags = [102]  # scale-covered torso
        node = parse_condition("Torso[has:fur-covered torso,scale-covered torso]")
        result = evaluate_condition(node, image_tags, self.all_groups)
        assert result is True
    
    def test_has_all_condition_true(self):
        image_tags = [301, 302]  # claws and fangs
        node = parse_condition("Features[has_all:claws,fangs]")
        result = evaluate_condition(node, image_tags, self.all_groups)
        assert result is True
    
    def test_has_all_condition_false(self):
        image_tags = [301]  # only claws
        node = parse_condition("Features[has_all:claws,fangs]")
        result = evaluate_condition(node, image_tags, self.all_groups)
        assert result is False
    
    def test_count_conditions(self):
        # Equal
        image_tags = [301, 302]  # 2 features
        assert evaluate_condition(
            parse_condition("Features[count=2]"), 
            image_tags, 
            self.all_groups
        ) is True
        
        # Greater or equal
        assert evaluate_condition(
            parse_condition("Features[count>=2]"), 
            image_tags, 
            self.all_groups
        ) is True
        
        # Greater
        assert evaluate_condition(
            parse_condition("Features[count>1]"), 
            image_tags, 
            self.all_groups
        ) is True
        
        # Less
        assert evaluate_condition(
            parse_condition("Features[count<3]"), 
            image_tags, 
            self.all_groups
        ) is True
    
    def test_and_operator(self):
        image_tags = [101, 201]  # torso and legs
        node = parse_condition("Torso[completed] AND Legs[completed]")
        result = evaluate_condition(node, image_tags, self.all_groups)
        assert result is True
        
        # One fails
        image_tags = [101]  # only torso
        result = evaluate_condition(node, image_tags, self.all_groups)
        assert result is False
    
    def test_or_operator(self):
        image_tags = [101]  # only torso
        node = parse_condition("Torso[completed] OR Legs[completed]")
        result = evaluate_condition(node, image_tags, self.all_groups)
        assert result is True
        
        # Both fail
        image_tags = []
        result = evaluate_condition(node, image_tags, self.all_groups)
        assert result is False
    
    def test_not_operator(self):
        image_tags = []
        node = parse_condition("NOT Torso[completed]")
        result = evaluate_condition(node, image_tags, self.all_groups)
        assert result is True
        
        image_tags = [101]
        result = evaluate_condition(node, image_tags, self.all_groups)
        assert result is False
    
    def test_complex_expression(self):
        # (Torso[completed] OR Legs[completed]) AND Features[count>=2]
        node = parse_condition(
            "(Torso[completed] OR Legs[completed]) AND Features[count>=2]"
        )
        
        # Has torso and 2 features - should be true
        image_tags = [101, 301, 302]
        assert evaluate_condition(node, image_tags, self.all_groups) is True
        
        # Has legs and 2 features - should be true
        image_tags = [201, 301, 302]
        assert evaluate_condition(node, image_tags, self.all_groups) is True
        
        # Has torso but only 1 feature - should be false
        image_tags = [101, 301]
        assert evaluate_condition(node, image_tags, self.all_groups) is False
        
        # Has neither torso nor legs - should be false
        image_tags = [301, 302]
        assert evaluate_condition(node, image_tags, self.all_groups) is False


class TestReferenceValidation:
    """Test validation of group and tag references"""
    
    def setup_method(self):
        """Set up test groups"""
        self.group1 = MockTagGroup(1, "First", 0, tags=[
            MockTag(101, "tag1"),
            MockTag(102, "tag2"),
        ])
        self.group2 = MockTagGroup(2, "Second", 1, tags=[
            MockTag(201, "tag3"),
        ])
        self.group3 = MockTagGroup(3, "Third", 2, tags=[
            MockTag(301, "tag4"),
        ])
        self.all_groups = [self.group1, self.group2, self.group3]
    
    def test_valid_reference_to_earlier_group(self):
        # Third group can reference First or Second
        node = parse_condition("First[completed]")
        validate_references(node, self.group3, self.all_groups)  # Should not raise
        
        node = parse_condition("Second[completed]")
        validate_references(node, self.group3, self.all_groups)  # Should not raise
    
    def test_invalid_reference_to_later_group(self):
        # First group cannot reference Second or Third
        node = parse_condition("Second[completed]")
        with pytest.raises(ValueError, match="must appear before"):
            validate_references(node, self.group1, self.all_groups)
    
    def test_invalid_reference_to_nonexistent_group(self):
        node = parse_condition("Nonexistent[completed]")
        with pytest.raises(ValueError, match="does not exist"):
            validate_references(node, self.group3, self.all_groups)
    
    def test_invalid_tag_reference(self):
        node = parse_condition("First[has:nonexistent_tag]")
        with pytest.raises(ValueError, match="does not exist in group"):
            validate_references(node, self.group3, self.all_groups)
    
    def test_valid_tag_reference(self):
        node = parse_condition("First[has:tag1]")
        validate_references(node, self.group3, self.all_groups)  # Should not raise
    
    def test_complex_expression_validation(self):
        # Valid complex expression
        node = parse_condition("First[has:tag1] AND Second[completed]")
        validate_references(node, self.group3, self.all_groups)  # Should not raise
        
        # Invalid - references later group
        node = parse_condition("First[completed] AND Third[completed]")
        with pytest.raises(ValueError):
            validate_references(node, self.group2, self.all_groups)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])