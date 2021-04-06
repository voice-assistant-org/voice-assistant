"""Host logic for assistant specific regular expressions.

These expressions are regex but allow to specify entity names.
Example:
  - r"what's the weather in <location>"
  - r"google for <<query>>"

Single brackets <> specify single word entities.
Double brackets <<>> specify entities of few words.

And-operator (&&) is also added on top of regex
Example:
   - "(a&&b)" is equivalent to "(?=.*(?:a))(?=.*(?:b))"
"""

import re
from typing import Dict, Optional, Tuple, Union

from voiceassistant.exceptions import NlpException
from voiceassistant.utils.datastruct import DottedDict

_ENTITY_REGEX = re.compile(r"(<{1,2}.*?>{1,2})")
_LONG_ENTITY_REGEX = re.compile(r"(<<\w+>>)")
_SHORT_ENTITY_REGEX = re.compile(r"(<\w+>)")

_LONG_ENTITY_REPLACE = r"(.*)"
_SHORT_ENTITY_REPLACE = r"([a-zA-Z0-9_]*)"

_AND_OPERATOR = "&&"
_AND_OPERATOR_PATTERN = re.compile(r"\(.*&&.*\)")


class _FixedEntityName(str):
    """Entity of a fixed number of words."""

    fixed = True


class _VariableEntityName(str):
    """Entity of a variable number of words."""

    fixed = False


EntityNameType = Union[_FixedEntityName, _VariableEntityName]


class NlpExprMatch:
    """Nlp expression match class."""

    def __init__(self, entity_names: Tuple[EntityNameType, ...]):  # noqa
        """Init."""
        self.entity_names = entity_names
        self.entities = DottedDict()

    def __str__(self) -> str:
        """Get object string representation."""
        return f"{self.entities}"

    def update_entities(self, new: Dict) -> None:
        """Update entities dictionary."""
        self.entities.update(new)

    def set_last_entity_end(self, end: int) -> None:
        """Set the position of last entity end."""
        self.last_entity_end = end


class NLPregexExpression:
    """NLP expression parser."""

    def __init__(self, expression: str, entities: Optional[Dict]):
        """Create NLP regex expression."""
        self.expression = self._validate_expression(expression)
        self.regex = self._get_expression_regex(expression)
        self.entity_names = self._get_entity_names(expression)
        self.hard_entities = self._preprocess_hard_entities(entities)

    def _validate_expression(self, expression: str) -> str:
        """Validate assistant NLP expression."""
        return expression

    def _get_expression_regex(self, expression: str) -> re.Pattern:
        """Generate compiled regex from expression."""
        interpretations = (
            self._interpret_entity_names,
            self._interpret_and_operator,
        )
        for interpretation in interpretations:
            expression = interpretation(expression)
        return re.compile(expression)

    def _interpret_entity_names(self, expression: str) -> str:
        """Convert entity names specified in expression into regex form."""
        regex = re.sub(_LONG_ENTITY_REGEX, _LONG_ENTITY_REPLACE, expression)
        return re.sub(_SHORT_ENTITY_REGEX, _SHORT_ENTITY_REPLACE, regex)

    def _interpret_and_operator(self, expression: str) -> str:
        """Convert expression with && operator into regex form."""
        match = _AND_OPERATOR_PATTERN.search(expression)
        if match:
            parts = match.group(0)[1:-1].split(_AND_OPERATOR)
            return "".join(f"(?=.*(?:{part}))" for part in parts)
        return expression

    def _preprocess_hard_entities(
        self, entities: Optional[Dict]
    ) -> Optional[Dict]:
        """Convert keys of hardcoded `entities` dict into _FixedEntityName."""
        if entities:
            for value in entities.values():
                if not isinstance(value, (tuple, list)):
                    raise NlpException(
                        "Entities must be specified as tuples or lists"
                    )
            return {_FixedEntityName(k): v for k, v in entities.items()}
        return None

    def _get_entity_names(self, expression: str) -> Tuple[EntityNameType, ...]:
        """Extract entity names from NLP regex expression."""
        return tuple(
            self._parse_entity_name(name)
            for name in _ENTITY_REGEX.findall(expression)
        )

    def _parse_entity_name(self, entity_name: str) -> EntityNameType:
        """Parse and derive a type of an entity name."""
        if entity_name[0:2] == "<<":
            return _VariableEntityName(entity_name.strip("<>"))
        else:
            return _FixedEntityName(entity_name.strip("<>"))

    def _find_hard_entities(self, text: str) -> DottedDict:
        """Find hardcoded entities from a `text`."""
        result = DottedDict()

        for name, keywords in self.hard_entities.items():  # type: ignore
            found = [ent for ent in keywords if ent in text]
            if found:
                result.update({name: found[0]})
        return result

    def match(self, text: str) -> Optional[NlpExprMatch]:
        """Match and extract entities from `text`."""
        matched = self.regex.search(text)

        if matched:
            nlp_expr_match = NlpExprMatch(entity_names=self.entity_names)
            entities = matched.groups()

            if entities:
                if len(entities) != len(self.entity_names):
                    raise NlpException("Matched unexpected number of entities")

                name_to_entity = dict(zip(self.entity_names, entities))
                nlp_expr_match.update_entities(name_to_entity)
                nlp_expr_match.set_last_entity_end(
                    matched.end(matched.lastindex)  # type: ignore
                )

            if self.hard_entities:
                nlp_expr_match.update_entities(self._find_hard_entities(text))

            return nlp_expr_match
        return None
