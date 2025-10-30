"""Liebherr Data Update Coordinator."""

from datetime import timedelta
import logging

from aiohttp import ClientSession
from pyliebherr import LiebherrAPI, LiebherrDevice

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.translation import async_get_translations
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL, DOMAIN

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

        update_interval: timedelta = timedelta(
            seconds=entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        )
        super().__init__(
            hass, _LOGGER, name="Liebherr Coordinator", update_interval=update_interval
        )

    async def _async_setup(self) -> None:
        """Set up the coordinator by getting devices."""
        self.data = await self.api.async_get_appliances()
        # get the zone translations here
        self.zone_translations = await async_get_translations(
            self.hass, self.hass.config.language, "common", [DOMAIN]
        )

    async def _async_update_data(self) -> list[LiebherrDevice]:
        """Fetch data from Liebherr API."""

        for device in self.data:
            _LOGGER.debug("Refreshing controls for device: %s", device.device_id)
            device.controls = await self.api.async_get_controls(device.device_id)
        return self.data
