"""Support for Liebherr autodoor devices with debounce logic."""

from enum import StrEnum
import logging

from pyliebherr import LiebherrControl, LiebherrDevice
from pyliebherr.const import CONTROL_TYPE
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
from .entity import LiebherrEntity

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

    entities: list[LiebherrCover] = []

    for device in config_entry.runtime_data.data:
        controls = device.controls
        if not controls:
            _LOGGER.warning("No controls found for appliance %s", device.device_id)
            continue

        for control in controls:
            if control.type == CONTROL_TYPE.AUTO_DOOR_CONTROL:
                entities.extend(
                    [LiebherrCover(config_entry.runtime_data, device, control)]
                )

    async_add_entities(entities, update_before_add=True)


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
    def available(self) -> bool:  # pyright: ignore[reportIncompatibleVariableOverride]
        """Overrride available in CoverEntity."""
        return super().available

    def _handle_coordinator_update(self) -> None:
        for control in self._device.controls:
            if (
                control.control_name == self._control.control_name
                and control.zone_id == self._control.zone_id
            ):
                if control.value != DOOR_STATE.MOVING:
                    self._attr_is_closed = control.value == DOOR_STATE.CLOSED
                    self._attr_is_closing = False
                    self._attr_is_opening = False
                    if control.value == DOOR_STATE.CLOSED:
                        self._last_state = STATE_CLOSED
                        self._attr_icon = "mdi:door"
                    else:
                        self._last_state = STATE_OPEN
                        self._attr_icon = "mdi:door-open"
                else:
                    self._attr_is_closed = False
                    self._attr_is_opening = self._last_state in [
                        STATE_CLOSED,
                        STATE_OPENING,
                    ]
                    self._attr_is_closing = self._last_state == [
                        STATE_OPEN,
                        STATE_CLOSING,
                    ]
                    self._last_state = (
                        STATE_OPENING if self._attr_is_opening else STATE_CLOSING
                    )
                break
        self.async_write_ha_state()

    async def async_open_cover(self, **kwargs):
        """Send command to open the cover."""
        await self.coordinator.api.async_set_value(
            self._device.device_id,
            AutoDoorControl(self._control.zone_id, True),
        )
        self._attr_is_opening = True
        self._attr_is_closing = False
        self._attr_is_closed = False
        self.async_write_ha_state()

    async def async_close_cover(self, **kwargs):
        """Send command to close the cover."""
        await self.coordinator.api.async_set_value(
            self._device.device_id,
            AutoDoorControl(self._control.zone_id, False),
        )
        self._attr_is_opening = False
        self._attr_is_closing = True
        self._attr_is_closed = False
        self.async_write_ha_state()
