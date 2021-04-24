# Voice Assistant
Customizable voice assistant
(README.md to be completed)

## Features
1. Trigger word can be said anywhere in a sentence, for example, "play music, Jarvis". It relies on [Picovoice porcupine](https://github.com/Picovoice/porcupine)
2. Speech-to-Text relies on [Google Cloud Speech-To-Text API](https://console.developers.google.com/apis/library/speech.googleapis.com/)
3. Text-to-Speech relies on [Amazon Polly](https://aws.amazon.com/polly/)

## Installation
1. Install Docker with [official guide](https://docs.docker.com/engine/install/debian/) or use convenience script (currently the only option for Raspbian):
   Uninstall old versions
   ```bash
   sudo apt-get remove docker docker-engine docker.io containerd runc
   ```
   Install using convenience script
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```
   
2. Create a folder to store configuration files e.g.
`mkdir ~/.voice-assistant`

3. Set up Google Cloud Speech-To-Text
 - Create Google Cloud Platform project and download your credentials following [instructions](https://cloud.google.com/docs/authentication/getting-started)
 -  Put credentials into your configuration folder `~/.voice-assistant/google_credentials.json`
 - Activate [Cloud Speech-To-Text API](https://console.developers.google.com/apis/library/speech.googleapis.com/) for your project

4. Set up AWS for Text-to-Speech
Create [AWS](https://aws.amazon.com/) account and take a note of Access Key ID and Secret
Access Key

5. Add `configuration.yaml` into `~/.voice-assistant/configuration.yaml`:
   ```yaml
    google_cloud:
      language_code: "en-US"

    aws:
      access_key_id: "YOUR_ACCES_KEY_ID"
      secret_access_key: "YOUR_SECRET_ACCESS_KEY"
      region_name: eu-west-2  # set closest to your location
      voice_id: "Brian"
    ```
 - `region_name` [list](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html)
 - `voice_id` [samples](https://eu-west-2.console.aws.amazon.com/polly/home/SynthesizeSpeech)

 6. Build Voice Assistant on Docker
 `sudo docker build -t voice-assistant .`


## Run on Docker
For convenience [Docker Compose](https://docs.docker.com/compose/install/) can be used:

Create `docker-compose.yaml`:
```yaml
version: '0.0.1'
services:
  voice-assistant:
    container_name: voice-assistant
    image: voice-assistant
    volumes:
      # volume to share config and credentials from host to container
      - your/configuration/folder:/usr/src/config
    devices:
      # sounds devices need to be exposed to container
      - /dev/snd:/dev/snd
    restart: always
```
Then run with `sudo docker-compose up` in the same folder.

