"""Download diagnostics."""

from dataclasses import asdict
import re
from typing import Any

import json

from homeassistant.components.diagnostics import REDACTED, async_redact_data
from homeassistant.const import (
    ATTR_ENTITY_PICTURE,
    ATTR_IDENTIFIERS,
    CONF_ACCESS_TOKEN,
    CONF_API_KEY,
    CONF_DEVICE_ID,
    CONF_UNIQUE_ID,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.device_registry as dr
import homeassistant.helpers.entity_registry as er

from .coordinator import LiebherrConfigEntry

TO_REDACT_CONFIG_ENTRY: list[str] = [CONF_API_KEY, CONF_DEVICE_ID]

TO_REDACT_DEVICE: list[str] = [ATTR_IDENTIFIERS]

TO_REDACT_STATE_ATTR: list[str] = [ATTR_ENTITY_PICTURE, CONF_ACCESS_TOKEN]

RE_REDACT_UNIQUE_ID = re.compile(r"(?<=liebherr_)(\d+\.*)+")


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: LiebherrConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""

    devices: list[dict[str, Any]] = [
        asdict(device) for device in entry.runtime_data.data
    ]

    return {
        "entry_config": {
            "version": f"{entry.version}.{entry.minor_version}",
            "data": async_redact_data(entry.data, TO_REDACT_CONFIG_ENTRY),
            "options": async_redact_data(entry.options, TO_REDACT_CONFIG_ENTRY),
        },
        "data": async_redact_data(devices, TO_REDACT_CONFIG_ENTRY),
    }


async def async_get_device_diagnostics(
    hass: HomeAssistant, config_entry: LiebherrConfigEntry, device: dr.DeviceEntry
) -> dict[str, Any]:
    """Return device-specific diagnostics."""
    data: dict[str, Any] = async_redact_data(device.dict_repr, TO_REDACT_DEVICE)

    entities: list[dict[str, Any]] = []
    for entry in er.async_entries_for_device(er.async_get(hass), device.id, True):
        dict_entry: dict[str, Any] = entry.as_partial_dict
        dict_entry[CONF_UNIQUE_ID] = RE_REDACT_UNIQUE_ID.sub(
            REDACTED, dict_entry[CONF_UNIQUE_ID]
        )
        if state := hass.states.get(entry.entity_id):
            if dict_entry["translation_key"] == "device_image":
                state_copy: dict[str, Any] = json.loads(state.as_dict_json)
                state_copy["attributes"] = async_redact_data(
                    state_copy["attributes"], TO_REDACT_STATE_ATTR
                )
                dict_entry["state"] = state_copy
            else:
                dict_entry["state"] = state.as_dict()
        entities.append(dict_entry)

    if entities:
        data["entities"] = entities

    return data
