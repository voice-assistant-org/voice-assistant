FROM python:3.8.8-buster

WORKDIR /usr/src

# Copy source code
COPY . voice-assistant/

# Install dependecies
RUN \
    apt-get update \
    && apt-get install -y libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 \
    python3-pyaudio mpg123 \
    && pip install --no-cache-dir -r voice-assistant/requirements.txt \
    && pip uninstall -y enum34 \ 
    && pip install --no-cache-dir -e ./voice-assistant \
    && python -m compileall voice-assistant/src/voiceassistant

# Set environmental variables
ENV \
    GOOGLE_APPLICATION_CREDENTIALS="/usr/src/config/google_credentials.json" \
    VOICE_ASSISTANT_CONFIGURATION="/usr/src/config/configuration.yaml"

# Application entry point
ENTRYPOINT ["python", "-m", "voiceassistant"]
