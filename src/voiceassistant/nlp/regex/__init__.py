"""Host regex based NL processor and skill wrapper."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, List, Optional

from voiceassistant.nlp.base import BaseNLP, NlpResult

from .expression import EntitiesDict, Expression

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant


class RegexIntent:
    """Store NLP regex intent related attributes."""

    def __init__(
        self, name: str, expressions: Iterable[str], entities: Optional[EntitiesDict] = None
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

    def __init__(self, vass: VoiceAssistant) -> None:
        """Init."""
        self._vass = vass
        self._intents: List[RegexIntent] = []

    def process(self, transcript: str) -> Optional[NlpResult]:
        """Process transcript by matching it to each skill."""
        for intent in self._intents:
            nlp_result = intent.match(transcript)
            if nlp_result:
                return nlp_result
        return None

    def add(self, intent: RegexIntent) -> None:
        """Add regex intent."""
        self._intents.append(intent)


__all__ = ["RegexNLP"]
