"""Spotify Integration."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, List

from voiceassistant.addons.create import Addon, CoreAttribute, addon_begin, addon_end
from voiceassistant.integrations.base import Integration
from voiceassistant.skills.create import Action, Skill, action, skill

from .client import VassSpotify
from .const import DEFAULT_MUFFLE_FACTOR, DEFAULT_VOLUME_INCREMENT, DOMAIN

if TYPE_CHECKING:
    from voiceassistant.config import Config
    from voiceassistant.core import VoiceAssistant
    from voiceassistant.interfaces.base import InterfaceIO
    from voiceassistant.utils.datastruct import DottedDict


CONF_MUFFLE_FACTOR = "volume_muffle_factor"
CONF_VOLUME_INCREMENT = "volume_increment"

CLIENT = "client"
VOLUME_LOWERED = "volume_lowered"
ORIGINAL_VOLUME = "original_volume"


def setup(vass: VoiceAssistant, config: Config) -> Integration:
    """Set up Spotify integration."""
    if not config[DOMAIN][CONF_MUFFLE_FACTOR]:
        config[DOMAIN][CONF_MUFFLE_FACTOR] = DEFAULT_MUFFLE_FACTOR

    if not config[DOMAIN][CONF_VOLUME_INCREMENT]:
        config[DOMAIN][CONF_VOLUME_INCREMENT] = DEFAULT_VOLUME_INCREMENT

    vass.data[DOMAIN] = {}
    vass.data[DOMAIN][CLIENT] = VassSpotify(vass, config)
    vass.data[DOMAIN][VOLUME_LOWERED] = False
    vass.data[DOMAIN][ORIGINAL_VOLUME] = 0

    return Spotify(vass, config)


class Spotify(Integration):
    """Spotify Integration."""

    name = DOMAIN

    def __init__(self, vass: VoiceAssistant, config: Config) -> None:
        """Init."""
        pass

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
def play(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Start playback."""
    vass.data[DOMAIN][CLIENT].play()
    interface.output("Let's go!")


@skill("music-pause")
def pause(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Pause playback."""
    vass.data[DOMAIN][CLIENT].pause()


@skill("music-next")
def play_next(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Switch to next track."""
    vass.data[DOMAIN][CLIENT].next()


@skill("music-previous")
def play_previous(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Switch to previous track."""
    vass.data[DOMAIN][CLIENT].previous()


@skill("music-volume-up")
def volume_up(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Increase volume."""
    volume_increment = vass.config[DOMAIN][CONF_VOLUME_INCREMENT]

    playback_volume = vass.data[DOMAIN][CLIENT].get_volume()
    if playback_volume is None:
        return

    volume = (
        vass.data[DOMAIN][ORIGINAL_VOLUME]
        if vass.data[DOMAIN][VOLUME_LOWERED]
        else playback_volume
    )

    if volume == 100:
        interface.output("Volume is already at maximum")
        return
    new_volume = volume + volume_increment
    new_volume = 100 if new_volume > 100 else new_volume
    vass.data[DOMAIN][CLIENT].set_volume(new_volume)
    vass.data[DOMAIN][ORIGINAL_VOLUME] = new_volume


@skill("music-volume-down")
def volume_down(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Decrease volume."""
    volume_increment = vass.config[DOMAIN][CONF_VOLUME_INCREMENT]

    playback_volume = vass.data[DOMAIN][CLIENT].get_volume()
    if playback_volume is None:
        return

    volume = (
        vass.data[DOMAIN][ORIGINAL_VOLUME]
        if vass.data[DOMAIN][VOLUME_LOWERED]
        else playback_volume
    )

    new_volume = volume - volume_increment
    new_volume = 0 if new_volume < 0 else new_volume
    vass.data[DOMAIN][CLIENT].set_volume(new_volume)
    vass.data[DOMAIN][ORIGINAL_VOLUME] = new_volume


@skill("music-set-volume")
def set_volume(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Set volume to a certain level."""
    new_volume = re.findall(r"\d+", entities.get("level", ""))

    if not new_volume:
        return
    vass.data[DOMAIN][CLIENT].set_volume(new_volume[0])
    vass.data[DOMAIN][ORIGINAL_VOLUME] = new_volume[0]
    interface.output(f"setting volume to {new_volume[0]}")


@skill("music-play-liked")
def play_liked(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Play liked tracks."""
    vass.data[DOMAIN][CLIENT].play_liked_tracks()
    interface.output("Favourites incoming")


@skill("music-play-similar")
def play_similar(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Play tracks similar to current."""
    vass.data[DOMAIN][CLIENT].play_similar_to_current()
    interface.output("here's something similar")


@skill("music-play-recommended")
def play_recommended_tracks(
    vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO
) -> None:
    """Play recommended tracks."""
    vass.data[DOMAIN][CLIENT].play_recommended_tracks()
    interface.output("here's recommended")


@skill("music-add-current-track")
def add_current_track(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Add curent track to liked."""
    vass.data[DOMAIN][CLIENT].add_current_track()
    interface.output("Great! Adding it to your library")


@skill("music-add-current-album")
def add_current_album(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Add current album to liked."""
    vass.data[DOMAIN][CLIENT].add_current_album()
    interface.output("Adding this album to your library")


@skill("music-play-current-artist")
def play_current_artist(
    vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO
) -> None:
    """Play tracks from currently playing artist."""
    vass.data[DOMAIN][CLIENT].play_current_track_artist()
    _say_track_description(vass, interface)


@skill("music-play-track")
def search_and_play_track(
    vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO
) -> None:
    """Search and play track."""
    track = entities.get("track")
    if track:
        vass.data[DOMAIN][CLIENT].search_and_play_track(track)
        _say_track_description(vass, interface)


@skill("music-play-album")
def search_and_play_album(
    vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO
) -> None:
    """Search and play album."""
    album = entities.get("album")
    if album:
        vass.data[DOMAIN][CLIENT].search_and_play_album(album)
        _say_track_description(vass, interface)


@skill("music-play-artist")
def search_and_play_artist(
    vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO
) -> None:
    """Search and play artist."""
    atrist = entities.get("artist")
    if atrist:
        vass.data[DOMAIN][CLIENT].search_and_play_artist(atrist)
        _say_track_description(vass, interface)


@skill("music-play-playlist")
def search_and_play_playlist(
    vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO
) -> None:
    """Search and play playlist."""
    playlist = entities.get("playlist")
    if playlist:
        vass.data[DOMAIN][CLIENT].search_and_play_playlist(playlist)
        _say_track_description(vass, interface)


@addon_begin(CoreAttribute.SPEECH_OUTPUT)
def lower_volume_output(vass: VoiceAssistant) -> None:
    """Lower volume when Voice Assistant is speaking."""
    _lower_volume(vass)


@addon_begin(CoreAttribute.SPEECH_PROCESSING)
def lower_volume_listen(vass: VoiceAssistant) -> None:
    """Lower volume when Voice Assistant is listening."""
    _lower_volume(vass)


@addon_end(CoreAttribute.SPEECH_OUTPUT)
def increase_volume_output(vass: VoiceAssistant) -> None:
    """Increase volume back when Voice Assistant stopped speaking."""
    _increase_volume_back(vass)


@addon_end(CoreAttribute.SPEECH_PROCESSING)
def increase_volume_listen(vass: VoiceAssistant) -> None:
    """Increase volume back when Voice Assistant stopped listening."""
    _increase_volume_back(vass)


@action("search_and_play")
def action_search_and_play(vass: VoiceAssistant, query: str, content_type: str) -> None:
    """Search and play action."""
    vass.data[DOMAIN][CLIENT].search_and_play(query, content_type)


def _say_track_description(vass: VoiceAssistant, interface: InterfaceIO) -> None:
    """Output current track description with a given `interface`."""
    track_description = vass.data[DOMAIN][CLIENT].get_current_track_description()
    if track_description:
        interface.output(f"Playing {track_description}")


def _lower_volume(vass: VoiceAssistant) -> None:
    """Lower Spotify volume."""
    muffle_factor = vass.config[DOMAIN][CONF_MUFFLE_FACTOR]

    if not vass.data[DOMAIN][VOLUME_LOWERED]:
        playback_volume = vass.data[DOMAIN][CLIENT].get_volume()
        if playback_volume is None:
            return
        vass.data[DOMAIN][ORIGINAL_VOLUME] = playback_volume
        vass.data[DOMAIN][CLIENT].set_volume(int(playback_volume * muffle_factor))
        vass.data[DOMAIN][VOLUME_LOWERED] = True


def _increase_volume_back(vass: VoiceAssistant) -> None:
    """Increase Spotify volume back to original value."""
    if vass.data[DOMAIN][VOLUME_LOWERED]:
        vass.data[DOMAIN][CLIENT].set_volume(vass.data[DOMAIN][ORIGINAL_VOLUME])
        vass.data[DOMAIN][VOLUME_LOWERED] = False


__all__ = ["Spotify"]
