"""Voice Assistant core components."""

import threading
from typing import Callable, List, Protocol

from voiceassistant.addons import AddonsComponent
from voiceassistant.integrations import IntegrationsComponent
from voiceassistant.interfaces import InterfacesComponent
from voiceassistant.nlp import NaturalLanguageComponent
from voiceassistant.skills import SkillsComponent
from voiceassistant.config import Config

VassJob = Callable[[], None]


class VoiceAssistant:
    """Voice Assistant root class."""

    _jobs: List[VassJob] = []

    def __init__(self) -> None:
        """Initialize Voice Assistant components.

        Order of initialization matters.
        """
        self.nlp: CoreComponent = NaturalLanguageComponent(self)
        self.interfaces: CoreComponent = InterfacesComponent(self)
        self.skills: CoreComponent = SkillsComponent(self)
        self.addons: CoreComponent = AddonsComponent(self)
        self.integrations: CoreComponent = IntegrationsComponent(self)

    def reload(self) -> None:
        Config.reload()
        components = (
            self.nlp,
            self.interfaces,
            self.skills,
            self.addons,
            self.integrations,
        )
        for component in components:
            component.load()

    def add_job(self, job: VassJob) -> None:
        """Add job for Voice Assistant to run."""
        self._jobs.append(job)

    def run(self) -> None:
        """Run Voice Assistant jobs in separate threads."""
        for job in self._jobs:
            threading.Thread(target=job).start()


__all__ = ["VoiceAssistant"]
