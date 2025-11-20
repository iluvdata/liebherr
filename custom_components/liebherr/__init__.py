"""Liebherr HomeAPI for HomeAssistant."""

import logging

from pyliebherr.exception import LiebherrAuthException

from homeassistant.components.hassio import async_get_clientsession
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed

from .coordinator import LiebherrConfigEntry, LiebherrCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = {
    Platform.CLIMATE,
    Platform.COVER,
    Platform.FAN,
    Platform.IMAGE,
    Platform.LIGHT,
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

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_migrate_entry(hass: HomeAssistant, config_entry: LiebherrConfigEntry):
    """Migrate old entry to newer version."""
    _LOGGER.debug(
        "Migrating configuration from version %s.%s",
        config_entry.version,
        config_entry.minor_version,
    )

    if config_entry.version == 1:
        if config_entry.minor_version < 2:
            # No longer using options for interval
            hass.config_entries.async_update_entry(
                config_entry, options={}, minor_version=2, version=1
            )

    _LOGGER.debug(
        "Migration to configuration version %s.%s successful",
        config_entry.version,
        config_entry.minor_version,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: LiebherrConfigEntry):
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
