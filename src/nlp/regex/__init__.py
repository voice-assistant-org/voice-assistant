"""Host regex based NL processor and skill wrapper."""

from typing import Optional

from ..nlp_result import NlpResult
from .skill import _REGEX_SKILLS, regex_skill


class NLPregexProcessor:
    """NL regex processor."""

    def process(self, transcript: str) -> Optional[NlpResult]:
        """Process transcript by matching it to each skill."""
        for skill in _REGEX_SKILLS:
            nlp_result = skill.match(transcript)
            if nlp_result:
                return nlp_result
        return None


__all__ = ["regex_skill", "NLPregexProcessor"]
