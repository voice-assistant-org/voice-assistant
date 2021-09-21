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
