"""Microphone audio stream implementation."""

from types import TracebackType
from typing import Dict, Generator, List, Tuple, Type

import pyaudio
from six.moves import queue

from voiceassistant.utils.datastruct import RollingWindowQueue


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate: int, chunk: int, rolling_window_sec: float = 3):
        """Create a microphone stream object."""
        self._rate = rate
        self._chunk = chunk

        # rolling window audio data buffer to store
        # the speech pronounced before the trigger word
        self._buff = RollingWindowQueue(
            size=int(rolling_window_sec * rate / chunk)
        )

        audio_interface = pyaudio.PyAudio()
        self._audio_stream = audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self._last_chunks: List[bytes] = []
        self.closed = False

    def __enter__(self):  # type: ignore
        """Start audio stream."""
        return self

    def __exit__(
        self,
        type: Type[BaseException],
        value: BaseException,
        traceback: TracebackType,
    ) -> None:
        """Stop audio stream."""
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)

    def _fill_buffer(
        self,
        in_data: bytes,
        frame_count: int,
        time_info: Dict,
        status_flags: int,
    ) -> Tuple:
        """Continuously collect data from the audio stream into the buffer."""
        self._buff.put(in_data)
        self._last_chunks.append(in_data)
        return None, pyaudio.paContinue

    def read(self) -> bytes:
        """Get chunk of audio bytes."""
        while not self._last_chunks:
            pass
        chunk = b"".join(self._last_chunks)
        self._last_chunks = []
        return chunk

    def generator(self) -> Generator[bytes, None, None]:
        """Continuously generate chunks of audio data."""
        self._buff.disable_size_limit()

        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            #  data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
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
