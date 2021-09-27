"""Voice Assistant core components."""

import threading
from typing import Any, Callable, Dict, List

import diskcache as dc

from voiceassistant.addons import AddonsComponent
from voiceassistant.const import CACHE_DIR
from voiceassistant.integrations import IntegrationsComponent
from voiceassistant.interfaces import InterfacesComponent
from voiceassistant.nlp import NaturalLanguageComponent
from voiceassistant.skills import SkillsComponent

VassJob = Callable[[], None]


class VoiceAssistant:
    """Voice Assistant root class."""

    _jobs: List[VassJob] = []
    data: Dict[str, Any] = {}  # data dict for components to share

    def __init__(self) -> None:
        """Initialize Voice Assistant components.

        Order of initialization matters.
        """
        self.cache = dc.Cache(CACHE_DIR)
        self.nlp = NaturalLanguageComponent(self)
        self.interfaces = InterfacesComponent(self)
        self.skills = SkillsComponent(self)
        self.addons = AddonsComponent(self)
        self.integrations = IntegrationsComponent(self)

    def add_job(self, job: VassJob) -> None:
        """Add job for Voice Assistant to run."""
        self._jobs.append(job)

    def run(self) -> None:
        """Run Voice Assistant jobs in separate threads."""
        for job in self._jobs:
            threading.Thread(target=job).start()


__all__ = ["VoiceAssistant"]
