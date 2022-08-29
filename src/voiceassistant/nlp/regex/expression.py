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
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

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
EntitiesDict = Union[Dict[str, List[str]], Dict[str, Tuple[str, ...]]]


@dataclass
class ExpressionMatch:
    """Nlp expression match class."""

    text: str
    entity_names: Tuple[EntityNameType, ...]
    entities: DottedDict
    last_entity_end: Optional[int]

    @property
    def is_complete(self) -> bool:
        """Determine if text has enough info to be processed."""
        # expression has no entities at all
        if not self.entity_names:
            return True

        # last matched entity is fixed
        if self.entity_names[-1].fixed:
            return True

        # all found entities are fixed
        if all(ent.fixed for ent in self.entity_names):
            return True

        # if string is longer than postion of last entity
        if self.last_entity_end and self.last_entity_end < len(self.text):
            return True

        return False


class Expression:
    """NLP expression parser."""

    def __init__(self, expression: str, entities: Optional[EntitiesDict] = None):
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

    def _preprocess_hard_entities(self, entities: Optional[EntitiesDict]) -> Optional[Dict]:
        """Convert keys of hardcoded `entities` dict into _FixedEntityName."""
        if entities:
            for value in entities.values():
                if not isinstance(value, (tuple, list)):
                    raise NlpException("Entities must be specified as tuples or lists")

            return {_FixedEntityName(k): re.compile("|".join(v)) for k, v in entities.items()}
        return None

    def _get_entity_names(self, expression: str) -> Tuple[EntityNameType, ...]:
        """Extract entity names from NLP regex expression."""
        return tuple(self._parse_entity_name(name) for name in _ENTITY_REGEX.findall(expression))

    def _parse_entity_name(self, entity_name: str) -> EntityNameType:
        """Parse and derive a type of an entity name."""
        if entity_name[0:2] == "<<":
            return _VariableEntityName(entity_name.strip("<>"))
        else:
            return _FixedEntityName(entity_name.strip("<>"))

    def _find_hard_entities(self, text: str) -> DottedDict:
        """Find hardcoded entities from a `text`."""
        result = DottedDict()

        for name, regex in self.hard_entities.items():  # type: ignore
            found = regex.search(text)
            if found:
                result.update({name: found[0]})
        return result

    def match(self, text: str) -> Optional[ExpressionMatch]:
        """Match and extract entities from `text`."""
        matched = self.regex.search(text)

        if matched:
            entities = DottedDict()
            entity_values = matched.groups()
            last_entity_end = None

            if entity_values:
                if len(entity_values) != len(self.entity_names):
                    raise NlpException("Matched unexpected number of entities")

                entities.update(dict(zip(self.entity_names, entity_values)))
                last_entity_end = matched.end(matched.lastindex)  # type: ignore

            if self.hard_entities:
                entities.update(self._find_hard_entities(text))

            return ExpressionMatch(
                text=text,
                entity_names=self.entity_names,
                entities=entities,
                last_entity_end=last_entity_end,
            )
        return None
