"""Liebherr Data Update Coordinator."""

from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Any

from pyliebherr import LiebherrAPI, LiebherrControls, LiebherrDevice
from pyliebherr.exception import (
    LiebherrAPILimitExceededException,
    LiebherrAuthException,
    LiebherrFetchException,
)
from pyliebherr.models import LiebherrControlRequest

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_POLL_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class LiebherrRuntimeData:
    """Holds the integration runtime data."""

    coordinators: list["LiebherrCoordinator"]
    translations: dict[str, str]


type LiebherrConfigEntry = ConfigEntry[LiebherrRuntimeData]


class LiebherrCoordinator(DataUpdateCoordinator[LiebherrControls]):
    """Liebherr Data Update Coordinator."""

    zone_translations: dict[str, str] = {}

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: LiebherrConfigEntry,
        api: LiebherrAPI,
        device: LiebherrDevice,
    ) -> None:
        """Initialize the coordinator."""

        self.config_entry: LiebherrConfigEntry = config_entry
        self.api: LiebherrAPI = api
        self.device: LiebherrDevice = device

        super().__init__(
            hass,
            _LOGGER,
            name=f"liebherr_coordinator_{device.device_id}",
            update_interval=timedelta(
                seconds=int(config_entry.options[CONF_POLL_INTERVAL])
            ),
        )

    async def _async_update_data(self) -> LiebherrControls:
        """Fetch data from Liebherr API."""
        try:
            self.data = await self.api.async_get_controls(self.device.device_id)
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
        return self.data

    async def async_set_value(
        self, control: LiebherrControlRequest
    ) -> list[dict[str, Any]]:
        """Perform Control Request on Device."""
        return await self.api.async_set_value(self.device.device_id, control)
