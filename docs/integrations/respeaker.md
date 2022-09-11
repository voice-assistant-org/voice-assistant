## Integration with ReSpeaker Microphones

ReSpeaker microphones are a good option to use with voice assistant. They come with LEDs installed on them which are great for providing light feedback just like Amazon Echo or Google Assistant. This is exactly what this integration aims to achieve.

Integration will try to automatically detect your respeaker microphone type once it is connected

#### Sample configuration entry
  ```yaml
   respeaker:
     pattern: echo
     brightness: 100
  ```

#### Config options:
- `pattern` - light pattern for respeaker microphone, currently supported options are `echo` and `google`
- `brightness` - brightness of respeaker microphone lights, value in [0, 100]


#### Tested microphones:
- [ReSpeaker 4-Mic Array for Raspberry Pi](https://wiki.seeedstudio.com/ReSpeaker_4_Mic_Array_for_Raspberry_Pi/)
- [ReSpeaker USB Mic Array v1](https://wiki.seeedstudio.com/ReSpeaker_Mic_Array/)