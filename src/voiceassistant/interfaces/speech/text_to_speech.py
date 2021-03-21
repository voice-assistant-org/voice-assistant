"""Text-to-speech component."""

import os

import boto3
from voiceassistant.utils.config import Config


class TextToSpeech:
    """Text to Speech class using Amazon Polly."""

    def __init__(self) -> None:
        """Create text-to-speech object."""
        self._audio_folder = self._get_audio_dir()
        self._client = boto3.Session(
            aws_access_key_id=Config.aws.access_key_id,
            aws_secret_access_key=Config.aws.secret_access_key,
            region_name=Config.aws.region_name,
        ).client("polly")

    def say(self, text: str) -> None:
        """Pronounce `text` with configured Polly voice.

        ToDo:
            Current implementation is bad and should later
            be changed to play audio bytes directly from memory.
        """
        self.synthesize_to_mp3_file(text, filename="speech")
        os.system(f"mpg123 {self._audio_folder}/speech.mp3 >/dev/null 2>&1")
        os.system(f"rm {self._audio_folder}/speech.mp3")

    def synthesize_to_mp3_file(self, text: str, filename: str) -> None:
        """Save synthesized `text` to mp3 file."""
        audio_bytes = self.synthesize(text, format="mp3")
        with open(f"{self._audio_folder}/{filename}.mp3", "wb") as file:
            file.write(audio_bytes)

    def synthesize(self, text: str, format: str = "mp3") -> bytes:
        """Synthesize `text` to audio bytes."""
        return self._client.synthesize_speech(  # type: ignore
            VoiceId=Config.aws.voice_id, OutputFormat=format, Text=text
        )["AudioStream"].read()
        # ogg_vorbis

    def _get_audio_dir(self) -> str:
        """Get audio directory for temporarily writing audio file."""
        dir = f"{os.path.expanduser('~')}/.voice-assistant"
        if not os.path.exists(dir):
            os.mkdir(dir)
        return dir
