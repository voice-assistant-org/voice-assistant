"""API app factory."""

from flask import Flask, Response, jsonify, request

from voiceassistant.exceptions import ConfigValidationError
from voiceassistant.nlp.regex import REGEX_SKILLS
from voiceassistant.utils.config import Config, set_assistant_config
from voiceassistant.utils.datastruct import DottedDict

from .auth import authorized


def api_factory(vass, app: Flask) -> Flask:  # type: ignore
    """Get REST API app."""
    name = "api"

    @app.route(f"/{name}/say", methods=["POST"])
    @authorized
    def say() -> Response:
        """Pronounce text.

        Sample payload:
        {"text": "Hello, World"}
        """
        payload = request.get_json() or {}
        try:
            vass.speech.output(payload["text"])
            return Response(status=200)
        except (KeyError, TypeError):
            return Response("Payload must have 'text' key", status=406)

    @app.route(f"/{name}/skills", methods=["GET"])
    @authorized
    def get_skills() -> Response:
        """Get an array of all available skill names."""
        skillnames = list(REGEX_SKILLS.keys())
        return jsonify(skillnames)

    @app.route(f"/{name}/skills/<skill_name>", methods=["GET", "POST"])
    @authorized
    def execute_skill(skill_name: str) -> Response:
        """Execure specified skill.

        Sample payload (Optional):
        {"entities": {"location": "Moscow"}}
        """
        payload = request.get_json() or {}
        try:
            entities = payload.get("entities", {})
            skill_func = REGEX_SKILLS[skill_name].func
            skill_func(entities=DottedDict(entities), interface=vass.speech)
            return Response(status=200)
        except KeyError:
            return Response(f"No such skill: {skill_name}", status=501)

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
            set_assistant_config(new_config)
            return Response(status=200)
        except ConfigValidationError:
            return Response("Invalid config", status=406)

    return app
