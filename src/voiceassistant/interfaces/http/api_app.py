"""API app factory."""

from __future__ import annotations

import random
import traceback
from typing import TYPE_CHECKING

from flask import Flask, Response, jsonify, request

from voiceassistant.config import Config
from voiceassistant.exceptions import ConfigValidationError, SkillError
from voiceassistant.utils.datastruct import DottedDict

from .auth import authorized

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant


def api_factory(vass: VoiceAssistant, app: Flask) -> Flask:
    """Get REST API app."""
    name = "api"

    @app.route(f"/{name}/say", methods=["POST"])
    @authorized
    def say() -> Response:
        """Pronounce text.

        Sample payload:
        {"text": "Hello, World"}
        """
        try:
            text = (request.get_json() or {})["text"]

            if isinstance(text, list):
                vass.interfaces.speech.output(random.choice(text))
            else:
                vass.interfaces.speech.output(text)

            return Response(status=200)
        except (KeyError, TypeError):
            return Response("Payload must have 'text' key", status=406)

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

    @app.route("/callback/<app>", methods=["GET"])
    def callback(app: str) -> Response:
        """Set callback request args to shared cache."""
        app_data = {app: request.args.to_dict()}

        if "callback" not in vass.data:
            vass.data["callback"] = app_data
        else:
            vass.data["callback"].update(app_data)

        return Response(
            f"<b>{app.capitalize()} setup is successful, you can close this tab</b>", status=200
        )

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

    return app
