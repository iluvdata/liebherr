"""Download diagnostics."""

from dataclasses import asdict
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_API_KEY, CONF_DEVICE_ID
from homeassistant.core import HomeAssistant

from .coordinator import LiebherrConfigEntry

TO_REDACT: list[str] = [CONF_API_KEY, CONF_DEVICE_ID]


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: LiebherrConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""

    devices: list[dict[str, Any]] = [
        asdict(device) for device in entry.runtime_data.data
    ]

    return {
        "entry_data": async_redact_data(entry.data, TO_REDACT),
        "options": async_redact_data(entry.options, TO_REDACT),
        "data": async_redact_data(devices, TO_REDACT),
    }
