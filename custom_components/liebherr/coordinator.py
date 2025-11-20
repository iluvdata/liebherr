"""Liebherr Data Update Coordinator."""

import asyncio
from datetime import timedelta
import logging

from aiohttp import ClientSession
from pyliebherr import LiebherrAPI, LiebherrDevice
from pyliebherr.exception import (
    LiebherrAPILimitExceededException,
    LiebherrAuthException,
    LiebherrFetchException,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.translation import async_get_translations
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

type LiebherrConfigEntry = ConfigEntry["LiebherrCoordinator"]


class LiebherrCoordinator(DataUpdateCoordinator[list[LiebherrDevice]]):
    """Liebherr Data Update Coordinator."""

    zone_translations: dict[str, str] = {}

    def __init__(
        self,
        hass: HomeAssistant,
        entry: LiebherrConfigEntry,
        client_session: ClientSession | None = None,
    ) -> None:
        """Initialize the coordinator."""
        self.api = LiebherrAPI(entry.data[CONF_API_KEY], client_session)

        update_interval: timedelta = timedelta(seconds=DEFAULT_UPDATE_INTERVAL)
        super().__init__(
            hass, _LOGGER, name="Liebherr Coordinator", update_interval=update_interval
        )

    async def _async_setup(self) -> None:
        """Set up the coordinator by getting devices."""
        try:
            self.data = await self.api.async_get_appliances()
        except LiebherrAuthException as ex:
            _LOGGER.error("Invalid API key")
            raise ConfigEntryAuthFailed(ex.message) from ex
        except LiebherrAPILimitExceededException as ex:
            _LOGGER.warning("API rate limit exceeded getting devices: %s", ex.message)
            raise UpdateFailed(
                translation_domain=DOMAIN, translation_key="api_limit_exceeded"
            ) from ex
        except LiebherrFetchException as ex:
            _LOGGER.error("Error fetching devices: %s", ex.message)
            raise UpdateFailed(ex.message) from ex
        # if there is more than one device, will need to slow the update interval to avoid rate limiting
        self.update_interval = timedelta(
            seconds=DEFAULT_UPDATE_INTERVAL * len(self.data)
        )
        self.zone_translations = await async_get_translations(
            self.hass, self.hass.config.language, "common", [DOMAIN]
        )

    async def _async_update_data(self) -> list[LiebherrDevice]:
        """Fetch data from Liebherr API."""

        for idx, device in enumerate(self.data):
            _LOGGER.debug("Refreshing controls for device: %s", device.device_id)
            try:
                device.controls = await self.api.async_get_controls(device.device_id)
                device.notify_listeners()
                if idx != len(self.data) - 1:
                    await asyncio.sleep(
                        DEFAULT_UPDATE_INTERVAL
                    )  # to avoid rate limiting
            except LiebherrAuthException as ex:
                _LOGGER.error("Invalid API key")
                raise ConfigEntryAuthFailed(ex.message) from ex
            except LiebherrAPILimitExceededException as ex:
                _LOGGER.warning(
                    "API rate limit exceeded getting devices: %s", ex.message
                )
                raise UpdateFailed(
                    translation_domain=DOMAIN, translation_key="api_limit_exceeded"
                ) from ex
            except LiebherrFetchException as ex:
                _LOGGER.error("Error fetching devices: %s", ex.message)
                raise UpdateFailed(ex.message) from ex
        return self.data
