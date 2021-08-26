"""Natural language handler subpackage."""

from types import TracebackType
from typing import TYPE_CHECKING, List, Type

from voiceassistant.utils.datastruct import RecognitionString

from .base import NlpResult
from .regex import NLPregexProcessor

if TYPE_CHECKING:
    from voiceassistant.interfaces.base import InterfaceIO


_NLP_PROCESSORS = (NLPregexProcessor(),)


class NaturalLanguageHandler:
    """Class to take action based on natural language text."""

    def __init__(self, interface: "InterfaceIO") -> None:
        """Init."""
        self.interface = interface

    def __enter__(self):  # type: ignore
        """Start natural language handler."""
        self._processed_results: List[NlpResult] = []
        self._last_text_length = 0
        return self

    def __exit__(
        self,
        type: Type[BaseException],
        value: BaseException,
        traceback: TracebackType,
    ) -> None:
        """Stop natural language processor."""
        pass

    def handle_next_transcript(self, transcript: RecognitionString) -> None:
        """Handle a sequence of transcripts.

        Usecase:
            Transcripts from continuos speech recognition.
            Each continuously recognized transcript is processed
            while user is speaking. Skill will be executed in two cases:
                1) transcript is complete (has enough information)
                2) transcript is final (user stopped speaking)
        """
        transcript = self._preprocess_transcript(transcript)

        for nlp_processor in _NLP_PROCESSORS:
            nlp_result = nlp_processor.process(transcript)

            if not nlp_result:
                continue

            if nlp_result in self._processed_results:
                continue

            if nlp_result.is_complete or transcript.is_final:
                self._make_record(transcript, nlp_result)
                nlp_result.execute_skill(interface=self.interface)

    def handle_single(self, transcript: str) -> None:
        """Handle a single transcript.

        Usecase: message from chatbot interface.
        """
        pass

    def _preprocess_transcript(
        self, text: RecognitionString
    ) -> RecognitionString:
        """Remove part of transcript that was already processed."""
        # fmt: off
        return RecognitionString(
            text[self._last_text_length:].lower(), is_final=text.is_final
        )
        # fmt: on

    def _make_record(
        self, transcript: RecognitionString, nlp_result: NlpResult
    ) -> None:
        """Make record of a processed transcript."""
        self._processed_results.append(nlp_result)
        self._last_text_length = len(transcript)


__all__ = ["NaturalLanguageHandler"]
