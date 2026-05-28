"""Support for Liebherr autodoor devices with debounce logic."""

from enum import StrEnum
import logging

from pyliebherr import LiebherrControlKey, LiebherrDevice
from pyliebherr.const import ControlType
from pyliebherr.models import AutoDoorControlRequest

from homeassistant.components.cover import (
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.core import HomeAssistant, callback

from . import LiebherrConfigEntry
from .entity import LiebherrEntity, base_async_setup_entry

_LOGGER = logging.getLogger(__name__)


class DoorState(StrEnum):
    """Liebherr door state."""

    CLOSED = "CLOSED"
    MOVING = "MOVING"
    OPEN = "OPEN"


async def async_setup_entry(
    hass: HomeAssistant, config_entry: LiebherrConfigEntry, async_add_entities
):
    """Set up Liebherr covers from a config entry."""

    await base_async_setup_entry(
        config_entry,
        async_add_entities,
        LiebherrCover,
        ControlType.AUTO_DOOR_CONTROL,
    )


class LiebherrCover(LiebherrEntity, CoverEntity):
    """Representation of a Liebherr auto door cover with debounce."""

    def __init__(
        self,
        config_entry: LiebherrConfigEntry,
        device: LiebherrDevice,
        control_key: LiebherrControlKey,
    ) -> None:
        """Initialize the cover entity."""
        super().__init__(config_entry, device, control_key)

        self._attr_device_class = CoverDeviceClass.DOOR
        self._attr_supported_features = (
            CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE
        )
        self._attr_icon = "mdi:door"
        self._last_state_closed: bool = self.control.value == DoorState.CLOSED
        # Defaults to true!?
        self._cover_is_last_toggle_direction_open = (
            self.control.value != DoorState.CLOSED
        )

    @callback
    def _async_write_ha_state(self) -> None:
        """Override for debugging logging only."""
        _LOGGER.debug(
            "Updating state for device %s zone %s\nclosed: %s, opening: %s, closing: %s",
            self.device.device_id,
            self.control.zone_id,
            self.is_closed,
            self.is_opening,
            self.is_closing,
        )
        super()._async_write_ha_state()

    @property
    def is_closed(self) -> bool:
        """Is closed."""
        if self.conrol.value in (DoorState.OPEN, DoorState.CLOSED):
            # Change only if the door isn't moving
            self._last_state_closed = self.control.value == DoorState.CLOSED
        return self.control.value == DoorState.CLOSED

    @property
    def is_opening(self) -> bool:
        """Is opening."""
        return self.control.value == DoorState.MOVING and self._last_state_closed

    @property
    def is_closing(self) -> bool:
        """Is Closing."""
        return self.control.value == DoorState.MOVING and (not self._last_state_closed)

    async def async_open_cover(self, **kwargs):
        """Send command to open the cover."""
        _LOGGER.debug(
            "Request open cover for device %s zone %s",
            self.device.device_id,
            self.control.zone_id,
        )
        await self.async_set_value(
            AutoDoorControlRequest(zoneId=self.control.zone_id, value=True),
        )
        self.control.value = DoorState.MOVING
        self.async_write_ha_state()

    async def async_close_cover(self, **kwargs):
        """Send command to close the cover."""
        _LOGGER.debug(
            "Request close cover for device %s zone %s",
            self.device.device_id,
            self.control.zone_id,
        )
        await self.async_set_value(
            AutoDoorControlRequest(zoneId=self.control.zone_id, value=False),
        )
        self.control.value = DoorState.MOVING
        self.async_write_ha_state()
