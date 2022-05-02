"""Microphone audio stream implementation."""

import collections
from types import TracebackType
from typing import Dict, Generator, Tuple, Type

import pyaudio
from six.moves import queue

_PAUSED = False


def pause_microphone_stream() -> None:
    """Pause microphone stream."""
    global _PAUSED
    _PAUSED = True


def resume_microphone_stream() -> None:
    """Resume microphone stream."""
    global _PAUSED
    _PAUSED = False


def microphone_is_paused() -> bool:
    """Return True if microphone stream is active."""
    global _PAUSED
    return _PAUSED


class MicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate: int, chunk: int, rolling_window_sec: float = 3):
        """Create a microphone stream object."""
        self._rate = rate
        self._chunk = chunk

        # rolling window audio data buffer to store
        # the speech pronounced before the trigger word
        self._prerecord_buff: collections.deque = collections.deque(
            maxlen=int(rolling_window_sec * rate / chunk)
        )
        self._buff: queue.Queue = queue.Queue()

        audio_interface = pyaudio.PyAudio()
        self._audio_stream = audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False

    def __enter__(self):  # type: ignore
        """Start audio stream."""
        return self

    def __exit__(
        self, type: Type[BaseException], value: BaseException, traceback: TracebackType
    ) -> None:
        """Stop audio stream."""
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)  # signal the generator to terminate

    def _fill_buffer(
        self,
        in_data: bytes,
        frame_count: int,
        time_info: Dict,
        status_flags: int,
    ) -> Tuple:
        """Continuously collect data from the audio stream into the buffer."""
        if not _PAUSED:
            self._buff.put(in_data)
            self._prerecord_buff.append(in_data)
        return None, pyaudio.paContinue

    def read(self) -> bytes:
        """Get chunk of all buffered audio bytes."""
        data = [self._buff.get(block=True)]

        # Now consume whatever other data's still buffered
        while True:
            try:
                data.append(self._buff.get(block=False))
            except queue.Empty:
                break

        return b"".join(data)

    def generator(self) -> Generator[bytes, None, None]:
        """Continuously generate chunks of audio data."""
        yield b"".join(self._prerecord_buff)  # pre-recorded audio chunk
        self._prerecord_buff.clear()

        while not self.closed:
            chunk = self._buff.get(block=True)
            if chunk is None:
                return

            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)
