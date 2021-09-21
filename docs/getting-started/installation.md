## Running in virtual environment (Python 3.6+)
1. Install dependencies:
	```bash
	sudo apt-get update
	sudo apt-get install -y libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 \
	python3-dev python3-pyaudio python3-venv mpg123
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
