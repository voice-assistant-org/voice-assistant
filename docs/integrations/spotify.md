## Integration with Spotify

#### Pre-requisites
You will need to register an application, follow official instructions [here](https://developer.spotify.com/documentation/web-api/quick-start/).

Even though not strictly required, it is convenient to run spotify player on the same device as voice assistant. For that consider using [raspotify](https://github.com/dtcooper/raspotify)

#### Sample configuration entry
  ```yaml
  spotify:
    client_id: <YOUR CLIENT ID>
    client_secret: <YOUR CLIENT SECRET>
    default_device: <NAME OF THE DEFAULT SPOTIFY DEVICE>
  ```
After configuration is done, reload voice assistant (e.g. by saying "reload yourself") and follow instructions printed in the shell/logs (currently the only way). This will be simplified once voice assistant has a web-ui

#### Config options:
- `client_id` (required) - can be found on your application dashboard
- `client_secret` (required) - can be found on your application dashboard
- `default_device` (required) - spotify device name to use as default e.g. your [raspotify](https://github.com/dtcooper/raspotify) player name or any other
- `volume_muffle_factor` (optional) - factor in [0,1] to multiply current volume when voice assistant is speaking or listening
- `volume_increment` (optional) - value in [0, 100] by which volume increases/decreases when you say "increase volume"