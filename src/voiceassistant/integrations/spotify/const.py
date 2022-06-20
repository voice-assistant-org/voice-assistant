"""Host constants for Spotify integration."""

DOMAIN = "spotify"

KEY_REFRESH_TOKEN = "spotify_refresh_token"

TYPE_TRACK = "track"
TYPE_ALBUM = "album"
TYPE_PLAYLIST = "playlist"
TYPE_ARTIST = "artist"

DEFAULT_MUFFLE_FACTOR = 0.5  # volume muffle factor
DEFAULT_VOLUME_INCREMENT = 20

URL_DEV_DASHBOARD = "https://developer.spotify.com/dashboard/applications"

MSG_NOT_PLAYING = "Spotify is not playing right now"
MSG_NO_DEVICE = "Spotify device ,{device}, is not available"
