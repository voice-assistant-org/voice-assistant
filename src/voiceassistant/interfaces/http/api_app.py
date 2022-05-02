"""API app factory."""

from __future__ import annotations

import random
import traceback
from typing import TYPE_CHECKING

from flask import Flask, Response, jsonify, request

from voiceassistant.config import Config
from voiceassistant.exceptions import ConfigValidationError, SkillError
from voiceassistant.utils import volume
from voiceassistant.utils.datastruct import DottedDict
from voiceassistant.utils.network import get_uuid
from voiceassistant.version import __version__

from .auth import authorized

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant


def api_factory(vass: VoiceAssistant, app: Flask) -> Flask:
    """Get REST API app."""
    name = "api"

    #
    # Actions
    #

    @app.route(f"/{name}/say", methods=["POST"])
    @authorized
    def say() -> Response:
        """Pronounce text.

        Sample payload:
        {"text": "Hello, World"}
        """
        try:
            payload = request.get_json() or {}
            text = payload["text"]
            cache = payload.get("cache", False)

            if isinstance(text, list):
                vass.interfaces.speech.output(random.choice(text), cache)
            else:
                vass.interfaces.speech.output(text, cache)

            return Response(status=200)
        except (KeyError, TypeError):
            return Response("Payload must have 'text' key", status=406)

    @app.route(f"/{name}/reload", methods=["GET"])
    @authorized
    def reload() -> Response:
        """Reload Voice Assistant components."""
        try:
            vass.load_components()
            return Response(status=200)
        except Exception:
            traceback.print_exc()
            return Response(status=500)

    @app.route(f"/{name}/trigger", methods=["GET"])
    @authorized
    def trigger() -> Response:
        """Trigger Voice Assistant."""
        vass.interfaces.speech.trigger()
        return Response(status=200)

    #
    # Skills
    #

    @app.route(f"/{name}/skills", methods=["GET"])
    @authorized
    def get_skills() -> Response:
        """Get an array of all available skill names."""
        return jsonify(vass.skills.names)

    @app.route(f"/{name}/skills/<skill_name>", methods=["GET", "POST"])
    @authorized
    def execute_skill(skill_name: str) -> Response:
        """Execure specified skill.

        Sample payload (Optional):
        {"entities": {"location": "Moscow"}}
        """
        payload = request.get_json() or {}
        try:
            vass.skills.run(
                name=skill_name,
                entities=DottedDict(payload.get("entities", {})),
                interface=vass.interfaces.speech,
            )
            return Response(status=200)
        except SkillError as e:
            return Response(str(e), status=501)

    #
    # Configuration
    #

    @app.route(f"/{name}/config", methods=["GET"])
    @authorized
    def get_config() -> Response:
        """Get Voice Assistant config."""
        return jsonify(Config)

    @app.route(f"/{name}/config", methods=["POST"])
    @authorized
    def set_config() -> Response:
        """Set Voice Assistant config.

        Payload must be a new config.
        """
        new_config = request.get_json() or {}
        try:
            Config.write(new_config)
            return Response(status=200)
        except ConfigValidationError:
            return Response("Invalid config", status=406)

    #
    # Internal
    #

    @app.route("/callback/<app>", methods=["GET"])
    def _callback(app: str) -> Response:
        """Set callback request args to shared cache."""
        app_data = {app: request.args.to_dict()}

        if "callback" not in vass.data:
            vass.data["callback"] = app_data
        else:
            vass.data["callback"].update(app_data)

        return Response(
            f"<b>{app.capitalize()} setup is successful, you can close this tab</b>", status=200
        )

    #
    # Info
    #

    @app.route(f"/{name}/info", methods=["GET"])
    @authorized
    def info() -> Response:
        """Get info about Voice Assistant."""
        info = {
            "name": Config.general.get("name", "undefined"),
            "version": __version__,
            "uuid": get_uuid(),
            "language": Config.general.get("language", "en"),
            "area": Config.general.get("area", "undefined"),
        }
        return jsonify(info)

    #
    # Volume controls
    #

    @app.route(f"/{name}/volume", methods=["GET"])
    @authorized
    def get_volume() -> Response:
        """Get host device volume."""
        return jsonify({"level": volume.get_volume(), "muted": volume.is_muted()})

    @app.route(f"/{name}/volume", methods=["POST"])
    @authorized
    def set_volume() -> Response:
        """Set host device volume."""
        payload = request.get_json() or {}
        volume.set_volume(payload["level"])
        return Response(status=200)

    @app.route(f"/{name}/mute", methods=["POST"])
    @authorized
    def set_mute() -> Response:
        """Set host device mute state."""
        payload = request.get_json() or {}
        volume.set_mute(payload["mute"])
        return Response(status=200)

    return app
