"""Liebherr HomeAPI for HomeAssistant."""

import logging
from typing import Any

from pyliebherr.exception import LiebherrAuthException

from homeassistant.components.hassio import async_get_clientsession
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import CONF_PRESENTATION_LIGHT_AS_SELECT
from .coordinator import LiebherrConfigEntry, LiebherrCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = {
    Platform.CLIMATE,
    Platform.COVER,
    Platform.FAN,
    Platform.IMAGE,
    Platform.SENSOR,
    Platform.SELECT,
    Platform.SWITCH,
}


async def async_setup_entry(hass: HomeAssistant, config_entry: LiebherrConfigEntry):
    """Set up Liebherr devices from a config entry."""

    coordinator: LiebherrCoordinator = LiebherrCoordinator(
        hass, config_entry, async_get_clientsession(hass)
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except LiebherrAuthException as ex:
        _LOGGER.error("Invalid API key, need to reauth")
        raise ConfigEntryAuthFailed(ex.message) from ex

    config_entry.runtime_data = coordinator

    if not config_entry.options.get(CONF_PRESENTATION_LIGHT_AS_SELECT, False):
        # Add Light to platforms
        PLATFORMS.add(Platform.LIGHT)

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_migrate_entry(hass: HomeAssistant, config_entry: LiebherrConfigEntry):
    """Migrate old entry to newer version."""

    if config_entry.version == 1:
        if config_entry.minor_version < 2:
            # No longer using options for interval, since reverted
            hass.config_entries.async_update_entry(
                config_entry, options={}, minor_version=2, version=1
            )
        if config_entry.minor_version < 3:
            # Add presentation_light_as_select option defaulting to False
            options: dict[str, Any] = config_entry.options.copy()
            options[CONF_PRESENTATION_LIGHT_AS_SELECT] = False
            hass.config_entries.async_update_entry(
                config_entry, options=options, minor_version=3, version=1
            )

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: LiebherrConfigEntry):
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, config_entry: LiebherrConfigEntry):
    """Remove a config entry."""
    return True
