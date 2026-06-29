"""Liebherr HomeAPI for HomeAssistant."""

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from pyliebherr import LiebherrAPI, LiebherrDevice
from pyliebherr.exception import (
    LiebherrAuthException,
    LiebherrException,
    LiebherrSSEException,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryError
from homeassistant.helpers.translation import async_get_translations
from homeassistant.util.ssl import client_context

from .const import CONF_PRESENTATION_LIGHT_AS_NUMBER, DOMAIN, SSE_INITIAL_TIMEOUT


@dataclass
class LiebherrRuntimeData:
    """Holds the integration runtime data."""

    api: LiebherrAPI
    devices: list[LiebherrDevice]
    translations: dict[str, str]


type LiebherrConfigEntry = ConfigEntry[LiebherrRuntimeData]


_LOGGER = logging.getLogger(__name__)

PLATFORMS = {
    Platform.CLIMATE,
    Platform.COVER,
    Platform.FAN,
    Platform.IMAGE,
    Platform.SELECT,
    Platform.SWITCH,
}


async def async_setup_entry(hass: HomeAssistant, config_entry: LiebherrConfigEntry):
    """Set up Liebherr devices from a config entry."""

    try:
        api: LiebherrAPI = LiebherrAPI(
            config_entry.data[CONF_API_KEY], ssl_context=client_context()
        )

        devices: list[LiebherrDevice] = await api.async_get_devices_wait_for_controls(
            timeout=SSE_INITIAL_TIMEOUT
        )

        def _get_device_error_callback(
            device: LiebherrDevice,
        ) -> Callable[[LiebherrSSEException], None]:

            sub_current_sse: Callable[[None], None] | None = None

            def _device_error_callback(exc: LiebherrSSEException) -> None:
                nonlocal sub_current_sse

                if device.reconnect_attempt < 10:
                    delay: int = 30 * device.reconnect_attempt
                    _LOGGER.info(
                        "Retrying SSE connection to %s after %ds delay, attempt %d",
                        device.device_id,
                        delay,
                        device.reconnect_attempt,
                    )
                    if sub_current_sse and callable(sub_current_sse):
                        sub_current_sse()  # Cancel the current task
                    sub_current_sse = api.start_sse(device, delay=delay)
                else:
                    raise ConfigEntryError(
                        translation_domain=DOMAIN,
                        translation_key="sse_error",
                        translation_placeholders={"attempt": device.reconnect_attempt},
                    )

            return _device_error_callback

        for device in devices:
            device.add_error_callback(_get_device_error_callback(device))

    except TimeoutError as ex:
        raise ConfigEntryError(
            translation_key="first_sse_timeout",
        ) from ex
    except LiebherrAuthException as ex:
        _LOGGER.error("Invalid API key, need to reauth")
        raise ConfigEntryAuthFailed(ex.message) from ex
    except LiebherrException as ex:
        raise ConfigEntryError(
            translation_key="config_entry", translation_placeholders={"msg": str(ex)}
        ) from ex

    config_entry.runtime_data = LiebherrRuntimeData(
        api=api,
        devices=devices,
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
        if config_entry.minor_version < 4:
            # Remove poll interval option
            options: dict[str, Any] = config_entry.options.copy()
            options.pop("poll_interval", None)
            hass.config_entries.async_update_entry(
                config_entry, options=options, minor_version=4, version=1
            )

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: LiebherrConfigEntry):
    """Unload a config entry."""
    await config_entry.runtime_data.api.async_close()
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, config_entry: LiebherrConfigEntry):
    """Remove a config entry."""
    return True
