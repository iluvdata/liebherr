"""Support for Liebherr autodoor devices with debounce logic."""

from enum import StrEnum
import logging

from pyliebherr import LiebherrControl, LiebherrDevice
from pyliebherr.const import ControlType
from pyliebherr.models import AutoDoorControl

from homeassistant.components.cover import (
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.const import (
    STATE_CLOSED,
    STATE_CLOSING,
    STATE_OPEN,
    STATE_OPENING,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant

from .coordinator import LiebherrConfigEntry, LiebherrCoordinator
from .entity import LiebherrEntity, base_async_setup_entry

_LOGGER = logging.getLogger(__name__)


class DOOR_STATE(StrEnum):
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
        coordinator: LiebherrCoordinator,
        device: LiebherrDevice,
        control: LiebherrControl,
    ) -> None:
        """Initialize the cover entity."""
        super().__init__(coordinator, device, control)

        self._attr_name = (
            f"{device.name} {control.control_name} {control.zone_position}"
        )
        self._attr_unique_id = (
            f"{device.device_id}_{control.control_name}_{control.zone_id}"
        )
        self._attr_device_class = CoverDeviceClass.DOOR
        self._attr_supported_features = (
            CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE
        )
        self._attr_icon = "mdi:door"
        # For debounce:
        self._last_state: str = STATE_UNKNOWN

    @property
    def is_closed(self) -> bool:
        """Is closed."""
        return self.control.value == DOOR_STATE.CLOSED

    @property
    def is_opening(self) -> bool:
        """Is opening."""
        return self.control.value == DOOR_STATE.MOVING and self._last_state in [
            STATE_CLOSED,
            STATE_OPENING,
        ]

    @property
    def is_closing(self) -> bool:
        """Is Closing."""
        return self.control.value == DOOR_STATE.MOVING and self._last_state in [
            STATE_OPEN,
            STATE_OPENING,
        ]

    def _handle_coordinator_update(self) -> None:
        self.__handle_coordinator_update(False)
        if self.control.value == DOOR_STATE.CLOSED:
            self._last_state = STATE_CLOSED
        elif self.control.value == DOOR_STATE.OPEN:
            self._last_state = STATE_OPEN
        elif self.control.value == DOOR_STATE.MOVING:
            if self._last_state in [STATE_CLOSED, STATE_OPENING]:
                self._last_state = STATE_OPENING
            elif self._last_state in [STATE_OPEN, STATE_CLOSING]:
                self._last_state = STATE_CLOSING
        self.async_write_ha_state()

    async def async_open_cover(self, **kwargs):
        """Send command to open the cover."""
        await self.async_set_value(
            AutoDoorControl(self.control.zone_id if self.control.zone_id else 0, True),
        )
        self._attr_is_opening = True
        self._attr_is_closing = False
        self._attr_is_closed = False
        self.async_write_ha_state()

    async def async_close_cover(self, **kwargs):
        """Send command to close the cover."""
        await self.async_set_value(
            AutoDoorControl(self.control.zone_id if self.control.zone_id else 0, False),
        )
        self._attr_is_opening = False
        self._attr_is_closing = True
        self._attr_is_closed = False
        self.async_write_ha_state()
