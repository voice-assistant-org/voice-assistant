"""Host regex skill struct."""
import warnings
from typing import Callable, Dict, Iterable, Optional, Set

from ..nlp_result import NlpResult
from .expression import NlpExprMatch, NLPregexExpression

REGEX_SKILLS = {}


def regex_skill(
    expressions: Iterable[str],
    entities: Optional[Dict] = None,
    name: Optional[str] = None,
) -> Callable:
    """Regex based skill wrapper."""

    def wrapper(func: Callable) -> Callable:
        skill_name = name or func.__name__
        if skill_name in REGEX_SKILLS:
            warnings.warn(
                f"Skill {skill_name} is already registered, skipping"
            )
        else:
            REGEX_SKILLS[skill_name] = RegexSkillStruct(
                name=skill_name,
                func=func,
                expressions=expressions,
                entities=entities,
            )
            print(f"Skill added: {skill_name}")
        return func

    return wrapper


class RegexSkillStruct:
    """Store regex skill related attributes."""

    def __init__(
        self,
        name: str,
        func: Callable,
        expressions: Iterable[str],
        entities: Optional[Dict] = None,
    ) -> None:
        """Create regex skill struct."""
        self.name = name
        self.func = func
        self.expressions = tuple(
            NLPregexExpression(expr, entities) for expr in expressions
        )

    def __str__(self) -> str:
        """Get string respresentation of self."""
        return f"Skill: {self.func.__name__}"

    def _get_all_entity_names(self) -> Set:
        """Get all skill related entity names."""
        return {ent for expr in self.expressions for ent in expr.entity_names}

    def _is_complete(self, text: str, match: NlpExprMatch) -> bool:
        """Determine if text has enough info to be processed."""
        # regex skill has no entities at all
        if not match.entity_names:
            return True
        # last matched entity is fixed
        if match.entity_names[-1].fixed:
            return True
        # all found entities are fixed
        if all(ent.fixed for ent in match.entity_names):
            return True
        # if string is longer than postion of last entity
        if match.last_entity_end < len(text):
            return True
        # all potential entities are present?
        # if self.all_entity_names == set(match.entities):
        #     return True
        return False

    def match(self, text: str) -> Optional[NlpResult]:
        """Match text to this skill."""
        for expr in self.expressions:
            expr_match = expr.match(text)
            if expr_match:
                return NlpResult(
                    skill_name=self.name,
                    skill_func=self.func,
                    entities=expr_match.entities,
                    is_complete=self._is_complete(text, expr_match),
                )
        return None
