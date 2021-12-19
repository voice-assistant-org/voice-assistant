## Integration: Home Assistant

### Prerequisites
If haven't already, enable [Home Assistant API](https://www.home-assistant.io/integrations/api/) and generate access token: in HASS Web UI click on your profile, scroll down to "Long-Lived Access Tokens" and click "create token".


## Setup
Put the following into Voice Assistant's `configuration.yaml`:
```yaml
hass:
  url: http://<your.hass.address>:8123
  token: <your_access_token>
```

## Skills

- `turn-on` </br>
Sample phrases: *turn on lights, lights on, enable lights, start computer*

- `turn-off` </br>
Sample phrases: *lights off, disable lights, turn off the fan*

- `open-cover` </br>
Sample phrases: *open blinds, blinds up, open curtains*

- `close-cover` </br>
Sample phrases: *close curtains*

To enable the above skills you must expose HASS entities first:
	
```yaml
hass:
  ...
  entities:
    - ids: # id(s) of hass entities
      - switch.bedroom_light_1
      - switch.bedroom_light_2
      names: # how you want to call a device in your phrase
      - lights
    - ids:
      - cover.curtain_bedroom
      names:
      - curtain
      - blinds
```

## Actions
- `hass.say_from_template`</br>
*template*

- `hass.call_service`</br>
*service*</br> 
*entity_id*</br>
*data*

- `hass.fire_event`</br>
*event_type*</br>
*event_data*</br>

- `hass.set_state`</br>
*entity_id*</br>
*state*</br>

- `hass.run_script`</br>
*script_id*</br>


	Consider an example:
```yaml
skills:
  ...
  - name: good_morning
    nlp:
      name: regex
      expressions:
      - good morning
      - (wake&&time)
    actions:
    - name: hass.run_script
      script_id: good_morning
    - name: hass.say_from_template
      template: Good Morning. The temperature outside is {{ state_attr('weather.my_home','temperature') }} degrees.
```
When user says *"good morning"* or  *"time to wake up"* Voice Assistant will execute two actions:
-  `run_script` - execute HASS script with id `good_morning`
-  `say_from_template` - say a phrase rendered by HASS Jinja2 template
