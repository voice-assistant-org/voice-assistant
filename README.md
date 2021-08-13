
# Voice Assistant
[![PyPI - Downloads](https://img.shields.io/pypi/dm/voiceassistant?style=flat-square)](https://pypistats.org/packages/voiceassistant)

Open-source customizable voice assistant

## Features
1. Trigger word can be said anywhere in a sentence, for example, *"play music, Jarvis"*. Few last seconds of audio input are recoded into memory, so when trigger word is said, pre-recorded audio data is also processed
2. Speech is processed continuously while user is speaking which, for certain requests, results in a very fast action/response
3. Integration with [Home Assistant](https://www.home-assistant.io/) REST API allows to define custom skills and link HASS entities via a simle config
4. Text-to-Speech relies on [Amazon Polly](https://aws.amazon.com/polly/) and allows to pick a custom voice from [available Polly voices](https://eu-west-2.console.aws.amazon.com/polly/home/SynthesizeSpeech)
5. Voice Assistant REST API enables remote control. For example, it can be used to make Voice Assistant say something when Home Assistant automation is triggered

## Running in virtual environment (Python 3.6+)
1. Install dependencies:
	```bash
	sudo apt-get update
	sudo apt-get install -y libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0\
	python3-pyaudio python3-venv mpg123
	```
2. Create virtual environment and install with pip:
	```bash
	python3 -m venv vass-venv
	source vass-venv/bin/activate
	pip install voiceassistant
	```
4. Start with command: `vass`

## Running on Docker

 [Docker Installation guide](https://docs.docker.com/engine/install/debian/). Raspbian only supports installation with [convenience script](https://docs.docker.com/engine/install/debian/#install-using-the-convenience-script).

1. Download and build Voice Assistant on Docker
	```bash
	git clone https://github.com/vadimtitov/voice-assistant
	cd voice-assistant
	docker build -t voice-assistant .
	```

2. Create a folder to store configuration files e.g.
	```bash
	mkdir -p ~/.config/voice-assistant
	```

3. Run with [Docker Compose](https://docs.docker.com/compose/install/):
- Create `docker-compose.yaml`:
	```yaml
  version: '1'
  services:
    voice-assistant:
      container_name: voice-assistant
      image: voice-assistant
      volumes:
        # volume to share config and credentials from host to container
        - <YOUR/CONFIGURATION/FOLDER>:/usr/src/config
      devices:
        # sounds devices need to be exposed to container
        - /dev/snd:/dev/snd
      restart: unless-stopped
      network_mode: host
	```
- Start with: `docker-compose up`

## First-time configuration
On the first start `configuration.yaml` and `google_credentials.json` files will be auto-generated inside voice assistant configuration folder. If running on Docker configuration folder path is chosen manually as per instructions above. If running in virtual environment, folder path is automatically chosen as `/home/<username>/.config/voiceassistant/`

As Voice Assistant relies on external engines for Speech-To-Text and Text-to-Speech the following needs to be set up:
1. Google Cloud Speech-To-Text
 - Create [Google Cloud Platform project](https://cloud.google.com/docs/authentication/getting-started), download and put your credentials as `google_credentials.json` inside configuration folder
 - [Activate Cloud Speech-To-Text API](https://console.developers.google.com/apis/library/speech.googleapis.com/) for your project

2. AWS for Text-to-Speech
- [Create AWS account](https://aws.amazon.com/) and take a note of Access Key ID and Secret Access Key
- Insert the above into `configuration.yaml`:
	```yaml
  tts:
    aws:
      access_key_id: "YOUR_ACCES_KEY_ID"
      secret_access_key: "YOUR_SECRET_ACCESS_KEY"
      ...
	```

## Customization
Currently the following customization options (YAML-paths) are available to specify in `configuration.yaml`:

- `triggerword.picovoice.word` - trigger word to use, the following words are available in [Picovoice porcupine](https://github.com/Picovoice/porcupine):
*alexa, americano, blueberry, bumblebee, computer, grapefruit, grasshopper, hey google, hey siri, jarvis, ok google, pico clock, picovoice, porcupine, smart mirror, snowboy, terminator, view glass*
- `triggerword.picovoice.sensitivity` - trigger word sensitivity, a number within [0, 1]
- `stt.google_cloud.language_code` - one of [language codes](https://cloud.google.com/speech-to-text/docs/languages) for STT
- `tts.aws.region_name` - one of [AWS region names]((https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html)), set closest to your location
- `tts.aws.voice_id` - one of [Polly Voice Samples](https://eu-west-2.console.aws.amazon.com/polly/home/SynthesizeSpeech)

## Integrating with Home Assistant
If haven't already, enable [Home Assistant API](https://www.home-assistant.io/integrations/api/) and generate access token: in HASS Web UI click on your profile, scroll down to "Long-Lived Access Tokens" and click "create token".

Add record to `configuration.yaml`:
```yaml
hass:
  url: http://<your.hass.address>:8123
  token: <your_access_token>
```

There are 2 types of integration with HASS:
1) Exposing HASS entities, for example:
	```yaml
	  hass:
	    ...
	    entities:
	      - ids:
	        - switch.bedroom_light_1
	        - switch.bedroom_light_2
	        names:
	        - lights
	      - ids:
	        - cover.curtain_bedroom
	        names:
	        - curtain
	        - blinds
	```

	The above sample configuration will allow user to control lights and blinds with the following phrases:
	- *turn on lights, lights on, enable lights, start lights, lights off, disable lights, etc*
	- *open blinds, blinds up, open curtains, close curtains, etc*

	Note that this only supports "binary" types of entities e.g. the ones that have `turn_on`-`turn_off` or `open_cover`-`close_cover` services.

2. Creating custom skills

	Custom skills can be defined by providing 3 things:
	1. Arbitrary skill `name`
	2. List of speech `expressions` that trigger the skill (can be regex)
	3. List of `actions` to execute when skill is triggered

	Currently available actions:
	| Action | Arguments |
	|--|--|
	| say_from_template | template  |
	|  call_service| service, entity_id, any additional data |
	| fire_event | event_type, event_data |
	| set_state | entity_id, state |
	| run_script | script_id |

	Consider an example:
	```yaml
	  hass:
	    ...
	    skills:
	      - name: good_morning
	        expressions:
	          - good morning
	          - (wake&&time)
	        actions:
	        - action: run_script
	          script_id: good_morning
	        - action: say_from_template
	          template: Good Morning. The temperature outside is {{ state_attr('weather.my_home','temperature') }} degrees.
	```
	When user says *"good morning"* or  *"time to wake up"* Voice Assistant will execute two actions:
	-  `run_script` - execute HASS script with id `good_morning`
	-  `say_from_template` - say a phrase rendered by HASS Jinja2 template
