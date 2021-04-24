"""Natural language processor component."""

from types import TracebackType
from typing import Optional, Set, Type

from voiceassistant import addons
from voiceassistant.interfaces import InterfaceType
from voiceassistant.interfaces.speech import RecognitionString

from .nlp_result import NlpResult
from .regex import NLPregexProcessor

NLP_PROCESSORS = (NLPregexProcessor(),)


class NaturalLanguageProcessor:
    """Natural language processor class."""

    @addons.call_at(start=addons.speech.processing_starts)
    def __enter__(self):  # type: ignore
        """Start natural language processor."""
        self._processed_results: Set[NlpResult] = set()
        self._last_text_length = 0
        return self

    @addons.call_at(end=addons.speech.processing_ends)
    def __exit__(
        self,
        type: Type[BaseException],
        value: BaseException,
        traceback: TracebackType,
    ) -> Optional[bool]:
        """Stop natural language processor."""
        pass

    def process_single(self, transcript: str) -> None:
        """Process a single transcript.

        Use case: message from chatbot interface.
        """
        pass

    def _make_record(
        self, transcript: RecognitionString, nlp_result: NlpResult
    ) -> None:
        """Make record of a processed transcript."""
        self._processed_results.add(nlp_result)
        self._last_text_length = len(transcript)

    def _preprocess_transcript(
        self, text: RecognitionString
    ) -> RecognitionString:
        """Remove part of transcript that was already processed."""
        # fmt: off
        return RecognitionString(
            text[self._last_text_length:].lower(), is_final=text.is_final
        )
        # fmt: on

    def process_next_transcript(
        self, transcript: RecognitionString, interface: InterfaceType
    ) -> None:
        """Process a sequence of transcripts.

        Usecase: transcripts from continuos speech recognition.
        Each continuously recognized transcript is processed
        while user is speaking. Skill will be executed in two cases:
            1) transcript is complete (has enough information)
            2) transcript is final (user stopped speaking)
        """
        transcript = self._preprocess_transcript(transcript)

        for nlp_processor in NLP_PROCESSORS:
            nlp_result = nlp_processor.process(transcript)

            if not nlp_result:
                continue

            if nlp_result in self._processed_results:
                continue

            if nlp_result.is_complete or transcript.is_final:
                self._make_record(transcript, nlp_result)
                nlp_result.execute_skill(interface=interface)
