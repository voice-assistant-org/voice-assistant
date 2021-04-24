"""Utils for customizable HASS actions."""

import copy
from typing import Callable, List

import hassapi

from voiceassistant.interfaces import InterfaceType
from voiceassistant.utils.datastruct import DottedDict


def make_skill_func(actions: List[DottedDict], hass: hassapi.Hass) -> Callable:
    """Build skill function for a list of `actions` from Config."""

    def _hass_actions(entities: DottedDict, interface: InterfaceType) -> None:
        """Run actions in a loop."""
        for action_data in copy.deepcopy(actions):
            action_name = action_data.pop("action")
            print(f"running action {action_name} with data:\n{action_data}")
            func = _ACTIONS[action_name]
            func(hass, interface, action_data)

    return _hass_actions


def _say_from_template(
    hass: hassapi.Hass, interface: InterfaceType, data: DottedDict
) -> None:
    """Render HASS Jinja2 template and output result via `interface`."""
    interface.output(hass.render_template(template=data.template))


def _call_service(
    hass: hassapi.Hass, interface: InterfaceType, data: DottedDict
) -> None:
    """Call HASS service."""
    hass.call_service(
        service=data.pop("service"), entity_id=data.pop("entity_id"), **data
    )


def _fire_event(
    hass: hassapi.Hass, interface: InterfaceType, data: DottedDict
) -> None:
    """Fire HASS event."""
    hass.fire_event(event_type=data.event_type, event_data=data.event_data)


def _set_state(
    hass: hassapi.Hass, interface: InterfaceType, data: DottedDict
) -> None:
    """Set state of a HASS entity."""
    hass.set_state(entity_id=data.entity_id, state=data.state)


def _run_script(
    hass: hassapi.Hass, interface: InterfaceType, data: DottedDict
) -> None:
    """Run HASS script."""
    hass.run_script(data.script_id)


_ACTIONS = {
    "say_from_template": _say_from_template,
    "call_service": _call_service,
    "fire_event": _fire_event,
    "set_state": _set_state,
    "run_script": _run_script,
}
