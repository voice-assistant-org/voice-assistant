## Integration with ReSpeaker Microphones

Integration will try to automatically detect your respeaker microphone type

#### Sample configuration entry
  ```yaml
   respeaker:
     pattern: echo
     brightness: 100
  ```

#### Config options:
- `pattern` - light pattern for respeaker microphone, currently supported options are `echo` and `google`
- `brightness` - brightness of respeaker microphone lights, value in [0, 100]
