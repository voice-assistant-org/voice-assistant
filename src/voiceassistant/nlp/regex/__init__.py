"""Host regex based NL processor and skill wrapper."""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Iterable, List, Optional

import yaml

from voiceassistant.config import Config
from voiceassistant.const import DATA_DIR
from voiceassistant.nlp.base import BaseNLP, NlpResult

from .expression import Expression

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant

NLP_DATAFILE = f"{DATA_DIR}/nlp/regex.yaml"


class RegexIntent:
    """Store NLP regex intent related attributes."""

    def __init__(
        self, name: str, expressions: Iterable[str], entities: Optional[Dict[str, str]] = None
    ) -> None:
        """Create regex skill struct."""
        self.name = name
        self.expressions = tuple(Expression(expr, entities) for expr in expressions)

    def match(self, text: str) -> Optional[NlpResult]:
        """Match text to this intent."""
        for expression in self.expressions:
            expression_match = expression.match(text)
            if expression_match:
                return NlpResult(
                    intent=self.name,
                    entities=expression_match.entities,
                    is_complete=expression_match.is_complete,
                )
        return None


class RegexNLP(BaseNLP):
    """NL regex processor."""

    name = "regex"
    _intents: List[RegexIntent] = []

    def __init__(self, vass: VoiceAssistant) -> None:
        """Init."""
        self._vass = vass
        # build in intents
        with open(NLP_DATAFILE) as file:
            self._intents.extend(RegexIntent(**intent) for intent in yaml.safe_load(file))

        # custom intents from config
        self._intents.extend(
            RegexIntent(
                name=skill["name"],
                expressions=skill["nlp"]["expressions"],
                entities=skill["nlp"].get("entities"),
            )
            for skill in Config.get("skills") or []
            if skill["nlp"]["name"] == self.name
        )

    def process(self, transcript: str) -> Optional[NlpResult]:
        """Process transcript by matching it to each skill."""
        for intent in self._intents:
            nlp_result = intent.match(transcript)
            if nlp_result:
                return nlp_result
        return None

    def add(
        self, name: str, expressions: Iterable[str], entities: Optional[Dict[str, str]] = None
    ) -> None:
        """Add regex intent."""
        self._intents.append(RegexIntent(name, expressions, entities))


__all__ = ["RegexNLP"]
