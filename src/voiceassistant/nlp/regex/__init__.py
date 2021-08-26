"""Host regex based NL processor and skill wrapper."""

from typing import Optional

from voiceassistant.nlp.base import BaseNLP, NlpResult

from .skill import REGEX_SKILLS, regex_skill


class NLPregexProcessor(BaseNLP):
    """NL regex processor."""

    def process(self, transcript: str) -> Optional[NlpResult]:
        """Process transcript by matching it to each skill."""
        for skill in REGEX_SKILLS.values():
            nlp_result = skill.match(transcript)
            if nlp_result:
                return nlp_result
        return None


__all__ = ["regex_skill", "NLPregexProcessor"]
