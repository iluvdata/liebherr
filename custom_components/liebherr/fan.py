"""Support for Liebherr HydroBreeze."""

from typing import Any

from pyliebherr import LiebherrControl, LiebherrDevice
from pyliebherr.const import ControlType
from pyliebherr.models import HydroBreezeControlRequest

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
)

from .coordinator import LiebherrConfigEntry, LiebherrCoordinator
from .entity import LiebherrEntity, base_async_setup_entry


def get_percent(mode: HydroBreezeControlRequest.HydroBreezeMode) -> int:
    """Covert mode to percent."""
    return ordered_list_item_to_percentage(
        list(HydroBreezeControlRequest.HydroBreezeMode), mode
    )


def get_mode(percent: int) -> HydroBreezeControlRequest.HydroBreezeMode:
    """Convert percent to mode."""
    return percentage_to_ordered_list_item(
        list(HydroBreezeControlRequest.HydroBreezeMode), percent
    )


async def async_setup_entry(
    hass: HomeAssistant, config_entry: LiebherrConfigEntry, async_add_entities
):
    """Set up Liebherr switches from a config entry."""

    await base_async_setup_entry(
        config_entry, async_add_entities, LiebherrFan, ControlType.HYDRO_BREEZE
    )


class LiebherrFan(LiebherrEntity, FanEntity):
    """Representation of a Liebherr switch entity."""

    def __init__(
        self,
        coordinator: LiebherrCoordinator,
        device: LiebherrDevice,
        control: LiebherrControl,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator, device, control)
        self._attr_icon = "mdi:fan-off"
        self._attr_speed_count = len(HydroBreezeControlRequest.HydroBreezeMode)
        self._attr_supported_features = (
            FanEntityFeature.TURN_OFF
            | FanEntityFeature.TURN_ON
            | FanEntityFeature.SET_SPEED
        )
        self._set_percentage()

    @property
    def is_on(self) -> bool:
        """Is on."""
        return self._mode != HydroBreezeControlRequest.HydroBreezeMode.OFF

    @property
    def _mode(self) -> HydroBreezeControlRequest.HydroBreezeMode:
        if self._control.current_mode and isinstance(
            self._control.current_mode, HydroBreezeControlRequest.HydroBreezeMode
        ):
            return self._control.current_mode
        return HydroBreezeControlRequest.HydroBreezeMode.OFF

    def _set_percentage(
        self,
    ) -> None:
        self._attr_percentage = get_percent(self._mode)

    def _handle_coordinator_update(self) -> None:
        super().__handle_coordinator_update(False)
        self._set_percentage()
        self.async_write_ha_state()

    async def _async_set_mode(
        self, mode: HydroBreezeControlRequest.HydroBreezeMode
    ) -> None:
        await self.coordinator.api.async_set_value(
            device_id=self._device.device_id,
            control=HydroBreezeControlRequest(
                mode, self._control.zone_id if self._control.zone_id else 0
            ),
        )
        self._control.currentMode = mode
        self._set_percentage()
        self.async_write_ha_state()

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn the fan on."""
        if percentage is not None:
            await self._async_set_mode(get_mode(percentage))
        else:
            await self._async_set_mode(HydroBreezeControlRequest.HydroBreezeMode.LOW)

    async def async_turn_off(self, **kwargs):
        """Turn the fan off."""
        await self._async_set_mode(HydroBreezeControlRequest.HydroBreezeMode.OFF)

    async def async_set_percentage(self, percentage: int) -> None:
        """Set speed."""
        if not percentage:
            return await self.async_turn_off()
        return await self.async_turn_on(percentage)
