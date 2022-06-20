"""Host Spotify integration."""

from __future__ import annotations

import contextlib
import random
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, ContextManager, Dict, Iterable, List, Optional

import tekore as tk

from voiceassistant.exceptions import ActionError, SetupIncomplete, UserCommunicateException

from .const import (
    DOMAIN,
    KEY_REFRESH_TOKEN,
    MSG_NO_DEVICE,
    MSG_NOT_PLAYING,
    TYPE_ALBUM,
    TYPE_ARTIST,
    TYPE_PLAYLIST,
    TYPE_TRACK,
    URL_DEV_DASHBOARD,
)

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant
    from voiceassistant.config import Config


class _SpotifyAuth:
    """Spotify Authorisation Client."""

    _token: Optional[tk.RefreshingToken] = None

    def __init__(self, vass: VoiceAssistant, config: Config) -> None:
        """Init."""
        self._vass = vass
        self._client = tk.Spotify()

        self._redirect_uri = f"{vass.interfaces.http.url}/callback/{DOMAIN}"
        self._credentials = tk.RefreshingCredentials(
            config.spotify.client_id,
            config.spotify.client_secret,
            redirect_uri=self._redirect_uri,
        )

        if self.refresh_token is None:  # user did not authorize
            self._user_auth = tk.UserAuth(self._credentials, tk.scope.every)
            self._prompt_user_login()

    @property
    def refresh_token(self) -> Optional[str]:
        """Return refresh token if it exists."""
        try:
            return self._vass.cache[KEY_REFRESH_TOKEN]  # type: ignore
        except KeyError:
            return None

    @property
    def token(self) -> tk.RefreshingToken:
        """Return self-refreshing token."""
        if self._token:
            return self._token

        if self.refresh_token:  # this will be used once on every app start
            new_token = self._credentials.refresh_user_token(self.refresh_token)
        else:  # this will be used once on the first start
            try:
                callback_data = self._vass.data["callback"][DOMAIN]
                code, state = callback_data["code"], callback_data["state"]
                new_token = self._user_auth.request_token(code, state)
            except KeyError:
                self._prompt_user_login()
                raise SetupIncomplete("Spotify login must be done, use link above")

        # cache refresh_token for the next app start
        self._vass.cache[KEY_REFRESH_TOKEN] = new_token.refresh_token

        self._token = new_token
        return self._token

    def _prompt_user_login(self) -> None:
        """Promt user with a spotify login link."""
        print(f"To use Spotify login into your account here: {self._user_auth.url}")
        print(f"Redirect uri: {self._redirect_uri}")
        print(f"Whitelist it here: {URL_DEV_DASHBOARD}")

    def new_token(self) -> ContextManager:
        """Return token-refreshing context manager."""
        return self._client.token_as(self.token)  # type: ignore


def auth(func: Callable) -> Callable:
    """Handle token refreshing for spotify methods."""

    @wraps(func)
    def auth_wrapper(self: "VassSpotify", *args: Any, **kwargs: Any) -> Any:
        with self.new_token():
            return func(self, *args, **kwargs)

    return auth_wrapper


def pick_device(func: Callable) -> Callable:
    """Pick device wrapper."""

    @wraps(func)
    def device_pick_wrapper(self: "VassSpotify", *args: Any, **kwargs: Any) -> Any:
        if not kwargs.get("device_id"):
            default = self.get_default_device_id()
            self._client.playback_transfer(default, force_play=True)
            kwargs["device_id"] = default

        return func(self, *args, **kwargs)

    return device_pick_wrapper


class VassSpotify(_SpotifyAuth):
    """Spotify client for Voice Assistant."""

    def __init__(self, vass: VoiceAssistant, config: Config) -> None:
        """Init."""
        _SpotifyAuth.__init__(self, vass, config)
        self._device_map: Dict[str, str] = {}
        self._default_device: str = config.spotify.default_device

    def get_default_device_id(self) -> str:
        """Return default device id."""
        return self.get_device_id(self._default_device)

    @auth
    def get_current_device(self) -> Optional[tk.model.Device]:
        """Return current device."""
        playback = self._client.playback()
        if playback:
            return playback.device
        return None

    @auth
    def get_devices(self) -> List[tk.model.Device]:
        """Return a list of currently active devices."""
        return self._client.playback_devices()  # type: ignore

    def get_device_id(self, name: str) -> str:
        """Get id of a device with `name`."""
        try:
            return self._device_map[name]
        except KeyError:
            self._device_map = {device.name: device.id for device in self.get_devices()}
        try:
            return self._device_map[name]
        except KeyError:
            raise UserCommunicateException(MSG_NO_DEVICE.format(device=name))

    @auth
    @pick_device
    def play(self, device_id: Optional[str] = None) -> None:
        """Continue playback if active or play recent tracks."""
        with contextlib.suppress(tk.Forbidden):
            if self._client.playback_currently_playing():
                self._client.playback_resume(device_id=device_id)
            else:
                self.play_recent_tracks(device_id=device_id)

    @auth
    @pick_device
    def pause(self, device_id: Optional[str] = None) -> None:
        """Pause current playback."""
        with contextlib.suppress(tk.Forbidden):
            self._client.playback_pause(device_id=device_id)

    @auth
    def toggle_play(self) -> None:
        """Toggle playback state."""
        playback = self._client.playback()
        if playback and playback.is_playing:
            self.pause()
        else:
            self.play()

    @auth
    @pick_device
    def play_tracks(
        self, tracks: Iterable[tk.model.Track], device_id: Optional[str] = None
    ) -> None:
        """Play `tracks` on `device`."""
        self._client.playback_start_tracks(
            track_ids=[track.id for track in tracks], device_id=device_id
        )

    @auth
    @pick_device
    def next(self, device_id: Optional[str] = None) -> None:
        """Switch to next track."""
        self._client.playback_next(device_id=device_id)

    @auth
    @pick_device
    def previous(self, device_id: Optional[str] = None) -> None:
        """Switch to previous track."""
        self._client.playback_previous(device_id=device_id)

    @auth
    @pick_device
    def play_recent_tracks(self, limit: int = 20, device_id: Optional[str] = None) -> None:
        """Play recent tracks."""
        recent_tracks = self._client.playback_recently_played(limit=limit).items
        self.play_tracks(ph.track for ph in recent_tracks)

    @auth
    @pick_device
    def play_liked_tracks(self, limit: int = 20, device_id: Optional[str] = None) -> None:
        """Play user liked tracks."""
        top_tracks = self._client.current_user_top_tracks(limit=limit).items
        random.shuffle(top_tracks)
        self.play_tracks(top_tracks)

    @auth
    @pick_device
    def play_saved_tracks(self, limit: int = 30, device_id: Optional[str] = None) -> None:
        """Play user saved tracks."""
        saved_tracks = self._client.saved_tracks(limit=limit).items
        random.shuffle(saved_tracks)
        self.play_tracks(saved.track for saved in saved_tracks)

    @auth
    @pick_device
    def play_recommended_tracks(self, limit: int = 30, device_id: Optional[str] = None) -> None:
        """Play user recommended tracks."""
        saved_tracks = self._client.saved_tracks(limit=limit).items
        saved_tracks = [s.track for s in saved_tracks]
        top_tracks = self._client.current_user_top_tracks(limit=limit).items

        mixed_tracks_ids = [t.id for t in top_tracks + saved_tracks]
        self.play_tracks(
            self._client.recommendations(
                track_ids=random.sample(mixed_tracks_ids, 5), limit=limit
            ).tracks
        )

    @auth
    @pick_device
    def play_similar_to_current(self, limit: int = 30, device_id: Optional[str] = None) -> None:
        """Play tracks that are similar to the current."""
        current = self._client.playback_currently_playing()
        if current:
            similar_tracks = self._client.recommendations(
                track_ids=[current.item.id], limit=limit
            ).tracks
            self.play_tracks(similar_tracks)
        else:
            raise UserCommunicateException(MSG_NOT_PLAYING)

    @auth
    @pick_device
    def play_current_track_artist(self, limit: int = 30, device_id: Optional[str] = None) -> None:
        """Play tracks by currently playing artist."""
        current = self._client.playback_currently_playing()
        if current:
            artist_uri = current.item.artists[0].uri
            self._client.playback_start_context(context_uri=artist_uri, device_id=device_id)
        else:
            raise UserCommunicateException(MSG_NOT_PLAYING)

    def play_made_for_me(self) -> None:
        """Play made for me tracks."""
        # ToDo
        raise NotImplementedError

    @auth
    def add_current_track(self) -> None:
        """Add current track to liked."""
        current = self._client.playback_currently_playing()
        if current:
            self._client.saved_tracks_add([current.item.id])
        else:
            raise UserCommunicateException(MSG_NOT_PLAYING)

    @auth
    def add_current_album(self) -> None:
        """Add current album to liked."""
        current = self._client.playback_currently_playing()
        if current:
            self._client.saved_albums_add([current.item.album.id])
        else:
            raise UserCommunicateException(MSG_NOT_PLAYING)

    @auth
    @pick_device
    def play_tracks_in_genre(
        self, genre: str, limit: int = 30, device_id: Optional[str] = None
    ) -> None:
        """Play tracks in a given `genre`.

        To see all genres use self.get_genres()
        """
        genre_tracks = self._client.recommendations(genres=[genre], limit=limit).tracks
        self.play_tracks(genre_tracks)

    def get_genres(self) -> List[str]:
        """Get genres available in Spotify."""
        return self._client.recommendation_genre_seeds()  # type: ignore

    def get_volume(self) -> Optional[int]:
        """Get current device volume."""
        device = self.get_current_device()
        if device:
            return device.volume_percent  # type: ignore
        return None

    @auth
    def set_volume(self, volume_percent: int, device_id: Optional[str] = None) -> None:
        """Set device volume (0..100)."""
        if device_id is None:
            try:
                device_id = self.get_device_id(self.get_current_device().name)
            except AttributeError:
                return

        with contextlib.suppress(tk.Forbidden):
            self._client.playback_volume(volume_percent=volume_percent, device_id=device_id)

    def search_and_play(self, query: str, content_type: str) -> None:
        """Search and play content from query."""
        methods = {
            "track": self.search_and_play_track,
            "album": self.search_and_play_album,
            "artist": self.search_and_play_artist,
            "playlist": self.search_and_play_playlist,
        }
        try:
            methods[content_type](query)
        except KeyError as e:
            raise ActionError(f"Invalid content_type {e}")

    @auth
    @pick_device
    def search_and_play_track(self, query: str, device_id: Optional[str] = None) -> None:
        """Search and play track from `query`."""
        self.play_tracks(
            [self._client.search(query=query, types=(TYPE_TRACK,), limit=1)[0].items[0]]
        )
        # TODO: add similar tracks to the queue

    @auth
    @pick_device
    def search_and_play_album(self, query: str, device_id: Optional[str] = None) -> None:
        """Search and play album from `query`."""
        uri = self._client.search(query=query, types=(TYPE_ALBUM,), limit=1)[0].items[0].uri
        self._client.playback_start_context(context_uri=uri, device_id=device_id)

    @auth
    @pick_device
    def search_and_play_playlist(self, query: str, device_id: Optional[str] = None) -> None:
        """Search and play playlist from `query`."""
        playlists = self._client.search(query=query, types=(TYPE_PLAYLIST,), limit=5)[0].items
        uri = random.choice(playlists).uri
        self._client.playback_start_context(context_uri=uri, device_id=device_id)

    @auth
    @pick_device
    def search_and_play_artist(self, query: str, device_id: Optional[str] = None) -> None:
        """Search and play artist from `query`."""
        uri = self._client.search(query=query, types=(TYPE_ARTIST,), limit=1)[0].items[0].uri
        self._client.playback_start_context(context_uri=uri, device_id=device_id)

    @auth
    def get_current_track_description(self) -> Optional[str]:
        """Get description of current track."""
        current = self._client.playback_currently_playing()
        if current and current.item:
            if len(current.item.artists) > 3:
                artists = f"{current.item.artists[0].name} and others"
            else:
                artists = ", ".join(a.name for a in current.item.artists)
            return f"{current.item.name} by {artists}"
        else:
            return None


__all__ = ["VassSpotify"]
