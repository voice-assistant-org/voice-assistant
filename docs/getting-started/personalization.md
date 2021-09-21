## Personalization
Currently the following customization options (YAML-paths) are available to specify in `configuration.yaml`:

- `triggerword.picovoice.word` - trigger word to use, the following words are available in [Picovoice porcupine](https://github.com/Picovoice/porcupine):
*alexa, americano, blueberry, bumblebee, computer, grapefruit, grasshopper, hey google, hey siri, jarvis, ok google, pico clock, picovoice, porcupine, smart mirror, snowboy, terminator, view glass*
- `triggerword.picovoice.sensitivity` - trigger word sensitivity, a number within [0, 1]
- `stt.google_cloud.language_code` - one of [language codes](https://cloud.google.com/speech-to-text/docs/languages) for STT
- `tts.aws.region_name` - one of [AWS region names]((https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html)), set closest to your location
- `tts.aws.voice_id` - one of [Polly Voice Samples](https://eu-west-2.console.aws.amazon.com/polly/home/SynthesizeSpeech)
