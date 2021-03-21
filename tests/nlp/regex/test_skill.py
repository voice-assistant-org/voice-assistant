import pytest
from voiceassistant.nlp.regex.skill import RegexSkillStruct


def dummy_skill_func():
    pass


@pytest.mark.parametrize(
    "expression, text, is_complete",
    [
        ("weather", "what's the weather", True),
        ("weather in <location>", "weather in London", True),
        ("weather in <<location>>", "weather in London", False),
        ("weather in <<location>> please", "weather in London please", True),
        (
            "weather in <<location>> on <weekday>",
            "weather in London on Sunday",
            True,
        ),
    ],
)
def test_is_complete(expression, text, is_complete):
    regex_skill = RegexSkillStruct(
        func=dummy_skill_func, expressions=[expression],
    )
    nlp_result = regex_skill.match(text)
    assert nlp_result
    assert nlp_result.is_complete == is_complete
