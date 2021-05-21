"""Text-to-speech component."""

import os

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError, NoCredentialsError

from voiceassistant import addons
from voiceassistant.const import DEFAULT_CONFIG_DIR
from voiceassistant.exceptions import SetupIncomplete
from voiceassistant.utils.config import Config


class TextToSpeech:
    """Text to Speech class using Amazon Polly."""

    def __init__(self) -> None:
        """Create text-to-speech object."""
        boto_config = BotoConfig(
            region_name=Config.aws.region_name,
            connect_timeout=0.7,
            read_timeout=0.7,
            parameter_validation=False,
        )
        self._client = boto3.Session(
            aws_access_key_id=Config.aws.access_key_id,
            aws_secret_access_key=Config.aws.secret_access_key,
        ).client(service_name="polly", config=boto_config)

        try:
            self._client.describe_voices()
        except (NoCredentialsError, ClientError):
            raise SetupIncomplete("Amazon Polly credentials not set")

    @addons.call_at(start=addons.speech.tts_starts, end=addons.speech.tts_ends)
    def say(self, text: str) -> None:
        """Pronounce `text` with configured Polly voice.

        ToDo:
            Current implementation is bad and should later
            be changed to play audio bytes directly from memory.
        """
        self.synthesize_to_mp3_file(text, filename="speech")
        os.system(f"mpg123 {DEFAULT_CONFIG_DIR}/speech.mp3 >/dev/null 2>&1")
        os.system(f"rm {DEFAULT_CONFIG_DIR}/speech.mp3")

    def synthesize_to_mp3_file(self, text: str, filename: str) -> None:
        """Save synthesized `text` to mp3 file."""
        audio_bytes = self.synthesize(text, format="mp3")
        with open(f"{DEFAULT_CONFIG_DIR}/{filename}.mp3", "wb") as file:
            file.write(audio_bytes)

    def synthesize(self, text: str, format: str = "mp3") -> bytes:
        """Synthesize `text` to audio bytes."""
        return self._client.synthesize_speech(  # type: ignore
            VoiceId=Config.aws.voice_id, OutputFormat=format, Text=text
        )["AudioStream"].read()
        # ogg_vorbis
