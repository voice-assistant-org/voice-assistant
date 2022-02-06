"""Voice Assistant core components."""

import threading
from typing import Any, Callable, Dict, List

import diskcache as dc

from voiceassistant.const import CACHE_DIR
from voiceassistant.exceptions import AssistantBaseException
from voiceassistant.interfaces import InterfacesComponent

VassJob = Callable[[], None]


class VoiceAssistant:
    """Voice Assistant root class."""

    def __init__(self) -> None:
        """Initialize Voice Assistant."""
        self._jobs: List[VassJob] = []
        self._is_running = False

        self.data: Dict[str, Any] = {}
        self.cache: dc.Cache = dc.Cache(CACHE_DIR)

        # interfaces must only be instantiated once, no reloading allowed
        self.interfaces = InterfacesComponent(self)

        # reloadable components
        self.load_components()

    def load_components(self) -> None:
        """Import and initialize Voice Assistant components.

        Importing is done here because we make sure that on every
        call this function reloads components' modules too.

        Order of initialization matters.
        """
        print("*** Loading Components ***")

        from voiceassistant.addons import AddonsComponent
        from voiceassistant.integrations import IntegrationsComponent
        from voiceassistant.nlp import NaturalLanguageComponent
        from voiceassistant.skills import SkillsComponent

        self.nlp = NaturalLanguageComponent(self)
        self.skills = SkillsComponent(self)
        self.addons = AddonsComponent(self)
        self.integrations = IntegrationsComponent(self)

    def add_job(self, job: VassJob) -> None:
        """Add job for Voice Assistant to run."""
        if self._is_running:
            raise AssistantBaseException("Cannot add job after Voice Assistant started running.")

        self._jobs.append(job)

    def run(self) -> None:
        """Run Voice Assistant jobs in separate threads."""
        self._is_running = True
        for job in self._jobs:
            threading.Thread(target=job).start()


__all__ = ["VoiceAssistant"]
