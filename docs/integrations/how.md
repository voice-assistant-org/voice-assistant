## Integrations
Integrations make sure Voice Assistant can work with external services or devices. The structure of integrations is such that they must provide one/few of 4 things: skills, actions, addons and extend the nlp "vocabulary".

### Skills and NLP
Skills are ready to use once integration is set up. They must work in combination with NLP expressions that trigger those skills.
For example, an integration with music service should allows you to say *"play music, Jarvis"*

### Actions
Action are routines that can be used to create your custom skills. Actions are named as "{integration name}.{action name}". For example, `hass` integration provides action `hass.say_from_template` which allows to render and pronounce any text using [Home Assistant Templating](https://www.home-assistant.io/docs/configuration/templating/)
```yaml
skills:
   ...
 - name: room-temperature
   nlp:
    - name: regex
      expressions:
      - (room&&temperature)
   actions:
     - name: hass.say_from_template
       template: The temperature in the room is {{ states('sensor.bedroom_temperature') }} degrees
```
### Addons
Addons extend the functionality of core components. For example, `respeaker` integration wraps keyword detector to start LED animation on a Respeaker microphone once keyword is detected.
