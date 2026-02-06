"""Liebherr HomeAPI for HomeAssistant."""

from asyncio import gather
import logging
from typing import Any

from pyliebherr import LiebherrAPI, LiebherrDevice
from pyliebherr.exception import LiebherrAuthException, LiebherrException

from homeassistant.components.hassio import async_get_clientsession
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryError
from homeassistant.helpers.translation import async_get_translations

from .const import (
    CONF_POLL_INTERVAL,
    CONF_PRESENTATION_LIGHT_AS_NUMBER,
    DOMAIN,
    MIN_UPDATE_INTERVAL,
)
from .coordinator import LiebherrConfigEntry, LiebherrCoordinator, LiebherrRuntimeData

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

    try:
        api: LiebherrAPI = LiebherrAPI(
            config_entry.data[CONF_API_KEY], async_get_clientsession(hass)
        )

        devices: list[LiebherrDevice] = await api.async_get_devices()

        # Verify the poll_interval > minimun
        if (
            config_entry.options[CONF_POLL_INTERVAL] / len(devices)
            < MIN_UPDATE_INTERVAL
        ):
            options: dict[str, Any] = {**config_entry.options}
            options[CONF_POLL_INTERVAL] = len(devices) * MIN_UPDATE_INTERVAL
            hass.config_entries.async_update_entry(config_entry, options=options)

        coordinators: list[LiebherrCoordinator] = [
            LiebherrCoordinator(hass, config_entry, api, device) for device in devices
        ]

        await gather(
            *[
                coordinator.async_config_entry_first_refresh()
                for coordinator in coordinators
            ]
        )

    except LiebherrAuthException as ex:
        _LOGGER.error("Invalid API key, need to reauth")
        raise ConfigEntryAuthFailed(ex.message) from ex
    except LiebherrException as ex:
        _LOGGER.exception("Error on integration setup")
        raise ConfigEntryError from ex

    config_entry.runtime_data = LiebherrRuntimeData(
        coordinators=coordinators,
        translations=await async_get_translations(
            hass, hass.config.language, "common", [DOMAIN]
        ),
    )

    if config_entry.options.get(CONF_PRESENTATION_LIGHT_AS_NUMBER, False):
        PLATFORMS.add(Platform.NUMBER)
    else:
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
            options[CONF_PRESENTATION_LIGHT_AS_NUMBER] = False
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
