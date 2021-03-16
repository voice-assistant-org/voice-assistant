import pytest
from src.nlp.regex.expression import NLPregexExpression


@pytest.mark.parametrize(
    "expression, text, expected_to_match",
    [("weather", "what's the weather", True), ("foo", "bar", False),],
)
def test_expression_match_matches(expression, text, expected_to_match):
    expr_match = NLPregexExpression(expression, entities=None).match(text)
    assert bool(expr_match) == expected_to_match


@pytest.mark.parametrize(
    "expression, text, expected_entities",
    [
        (
            "weather in <location>",
            "what's the weather in London mate",
            {"location": "London"},
        ),
    ],
)
def test_expression_match_finds_entities(expression, text, expected_entities):
    expr_match = NLPregexExpression(expression, entities=None).match(text)
    assert expr_match
    assert expr_match.entities == expected_entities


@pytest.mark.parametrize(
    "expression, text, expected_last_entity_end",
    [("weather in <<location>> please", "weather in London please", 17),],
)
def test_expression_match_finds_last_endity_end(
    expression, text, expected_last_entity_end
):
    expr_match = NLPregexExpression(expression, entities=None).match(text)
    assert expr_match
    assert expr_match.last_entity_end == expected_last_entity_end
