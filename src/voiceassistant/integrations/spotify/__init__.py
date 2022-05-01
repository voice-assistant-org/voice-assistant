"""Spotify Integration."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, List

from voiceassistant.addons.create import Addon, CoreAttribute, addon_begin, addon_end
from voiceassistant.config import Config
from voiceassistant.integrations.base import Integration
from voiceassistant.skills.create import Action, Skill, action, skill

from .client import VassSpotify
from .const import NAME, VOLUME_INCREMENT, VOLUME_MUFFLE_FACTOR

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant
    from voiceassistant.interfaces.base import InterfaceIO
    from voiceassistant.utils.datastruct import DottedDict

_MUFFLE_FACTOR = Config.spotify.get("volume_muffle_factor") or VOLUME_MUFFLE_FACTOR
_VOLUME_INCREMENT = Config.spotify.get("volume_increment") or VOLUME_INCREMENT

_spotify: VassSpotify = None  # type: ignore
_volume_lowered: bool = False
_original_volume: int = 0


class Spotify(Integration):
    """Spotify Integration."""

    name = NAME

    def __init__(self, vass: VoiceAssistant) -> None:
        """Initialize base client as global var."""
        global _spotify
        _spotify = VassSpotify(vass)

    @property
    def actions(self) -> List[Action]:
        """Return list of spotify actions."""
        return [
            action_search_and_play,
        ]

    @property
    def skills(self) -> List[Skill]:
        """Return list of spotify skills."""
        return [
            play,
            pause,
            play_next,
            play_previous,
            volume_up,
            volume_down,
            set_volume,
            play_liked,
            play_similar,
            play_recommended_tracks,
            add_current_track,
            add_current_album,
            play_current_artist,
            search_and_play_track,
            search_and_play_album,
            search_and_play_artist,
            search_and_play_playlist,
        ]

    @property
    def addons(self) -> List[Addon]:
        """Return list of spotify addons."""
        return [
            lower_volume_output,
            lower_volume_listen,
            increase_volume_output,
            increase_volume_listen,
        ]


@skill("music-play")
def play(entities: DottedDict, interface: InterfaceIO) -> None:
    """Start playback."""
    _spotify.play()
    _say_track_description(interface)


@skill("music-pause")
def pause(entities: DottedDict, interface: InterfaceIO) -> None:
    """Pause playback."""
    _spotify.pause()


@skill("music-next")
def play_next(entities: DottedDict, interface: InterfaceIO) -> None:
    """Switch to next track."""
    _spotify.next()


@skill("music-previous")
def play_previous(entities: DottedDict, interface: InterfaceIO) -> None:
    """Switch to previous track."""
    _spotify.previous()


@skill("music-volume-up")
def volume_up(entities: DottedDict, interface: InterfaceIO) -> None:
    """Increase volume."""
    global _original_volume, _volume_lowered

    playback_volume = _spotify.get_volume()
    if playback_volume is None:
        return

    volume = _original_volume if _volume_lowered else playback_volume

    if volume == 100:
        interface.output("Volume is already at maximum")
        return
    new_volume = volume + _VOLUME_INCREMENT
    new_volume = 100 if new_volume > 100 else new_volume
    _spotify.set_volume(new_volume)
    _original_volume = new_volume


@skill("music-volume-down")
def volume_down(entities: DottedDict, interface: InterfaceIO) -> None:
    """Decrease volume."""
    global _original_volume, _volume_lowered

    playback_volume = _spotify.get_volume()
    if playback_volume is None:
        return

    volume = _original_volume if _volume_lowered else playback_volume

    new_volume = volume - _VOLUME_INCREMENT
    new_volume = 0 if new_volume < 0 else new_volume
    _spotify.set_volume(new_volume)
    _original_volume = new_volume


@skill("music-set-volume")
def set_volume(entities: DottedDict, interface: InterfaceIO) -> None:
    """Set volume to a certain level."""
    global _original_volume
    new_volume = re.findall(r"\d+", entities.get("level", ""))

    if not new_volume:
        return
    _spotify.set_volume(new_volume[0])
    _original_volume = new_volume[0]


@skill("music-play-liked")
def play_liked(entities: DottedDict, interface: InterfaceIO) -> None:
    """Play liked tracks."""
    _spotify.play_liked_tracks()


@skill("music-play-similar")
def play_similar(entities: DottedDict, interface: InterfaceIO) -> None:
    """Play tracks similar to current."""
    _spotify.play_similar_to_current()
    _say_track_description(interface)


@skill("music-play-recommended")
def play_recommended_tracks(entities: DottedDict, interface: InterfaceIO) -> None:
    """Play recommended tracks."""
    _spotify.play_recommended_tracks()
    _say_track_description(interface)


@skill("music-add-current-track")
def add_current_track(entities: DottedDict, interface: InterfaceIO) -> None:
    """Add curent track to liked."""
    _spotify.add_current_track()
    interface.output("Great! Adding it to your library")


@skill("music-add-current-album")
def add_current_album(entities: DottedDict, interface: InterfaceIO) -> None:
    """Add current album to liked."""
    _spotify.add_current_album()
    interface.output("Adding this album to your library")


@skill("music-play-current-artist")
def play_current_artist(entities: DottedDict, interface: InterfaceIO) -> None:
    """Play tracks from currently playing artist."""
    _spotify.play_current_track_artist()


@skill("music-play-track")
def search_and_play_track(entities: DottedDict, interface: InterfaceIO) -> None:
    """Search and play track."""
    track = entities.get("track")
    if track:
        _spotify.search_and_play_track(track)
        _say_track_description(interface)


@skill("music-play-album")
def search_and_play_album(entities: DottedDict, interface: InterfaceIO) -> None:
    """Search and play album."""
    album = entities.get("album")
    if album:
        _spotify.search_and_play_album(album)
        _say_track_description(interface)


@skill("music-play-artist")
def search_and_play_artist(entities: DottedDict, interface: InterfaceIO) -> None:
    """Search and play artist."""
    atrist = entities.get("artist")
    if atrist:
        _spotify.search_and_play_artist(atrist)
        _say_track_description(interface)


@skill("music-play-playlist")
def search_and_play_playlist(entities: DottedDict, interface: InterfaceIO) -> None:
    """Search and play playlist."""
    playlist = entities.get("playlist")
    if playlist:
        _spotify.search_and_play_playlist(playlist)
        _say_track_description(interface)


@addon_begin(CoreAttribute.SPEECH_OUTPUT)
def lower_volume_output(vass: VoiceAssistant) -> None:
    """Lower volume when Voice Assistant is speaking."""
    _lower_volume()


@addon_begin(CoreAttribute.SPEECH_PROCESSING)
def lower_volume_listen(vass: VoiceAssistant) -> None:
    """Lower volume when Voice Assistant is listening."""
    _lower_volume()


@addon_end(CoreAttribute.SPEECH_OUTPUT)
def increase_volume_output(vass: VoiceAssistant) -> None:
    """Increase volume back when Voice Assistant stopped speaking."""
    _increase_volume_back()


@addon_end(CoreAttribute.SPEECH_PROCESSING)
def increase_volume_listen(vass: VoiceAssistant) -> None:
    """Increase volume back when Voice Assistant stopped listening."""
    _increase_volume_back()


@action("search_and_play")
def action_search_and_play(query: str, content_type: str) -> None:
    """Search and play action."""
    _spotify.search_and_play(query, content_type)


def _say_track_description(interface: InterfaceIO) -> None:
    """Output current track description with a given `interface`."""
    track_description = _spotify.get_current_track_description()
    if track_description:
        interface.output(f"Playing {track_description}")


def _lower_volume() -> None:
    """Lower Spotify volume."""
    global _volume_lowered, _original_volume
    if not _volume_lowered:
        playback_volume = _spotify.get_volume()
        if playback_volume is None:
            return
        _original_volume = playback_volume
        _spotify.set_volume(int(_original_volume * _MUFFLE_FACTOR))
        _volume_lowered = True


def _increase_volume_back() -> None:
    """Increase Spotify volume back to original value."""
    global _volume_lowered, _original_volume
    if _volume_lowered:
        _spotify.set_volume(_original_volume)
        _volume_lowered = False


__all__ = ["Spotify"]
