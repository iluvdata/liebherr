"""Support for Liebherr HydroBreeze."""

import logging
from typing import Any, cast

from pyliebherr import LiebherrControl, LiebherrDevice
from pyliebherr.const import CONTROL_TYPE
from pyliebherr.models import HydroBreezeControlRequest

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
)

from .coordinator import LiebherrConfigEntry, LiebherrCoordinator
from .entity import LiebherrEntity

_LOGGER = logging.getLogger(__name__)


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

    entities = []
    for device in config_entry.runtime_data.data:
        controls: list[LiebherrControl] = device.controls
        if not controls:
            _LOGGER.warning("No controls found for appliance %s", device.device_id)
            continue

        for control in controls:
            if control.type == CONTROL_TYPE.HYDRO_BREEZE:
                entities.extend(
                    [
                        LiebherrFan(config_entry.runtime_data, device, control),
                    ]
                )

    async_add_entities(entities, update_before_add=True)


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
        self._attr_icon = "mdi:fan"
        self._attr_speed_count = len(HydroBreezeControlRequest.HydroBreezeMode)
        self._attr_supported_features = (
            FanEntityFeature.TURN_OFF
            | FanEntityFeature.TURN_ON
            | FanEntityFeature.SET_SPEED
        )

    @property
    def available(self) -> bool:  # pyright: ignore[reportIncompatibleVariableOverride, reportIncompatibleMethodOverride]
        """Available."""
        return super().available

    def _handle_device_update(self) -> None:
        for control in self._device.controls:
            if (
                control.control_name == self._control.control_name
                and control.zone_id == self._control.zone_id
            ):
                mode: HydroBreezeControlRequest.HydroBreezeMode = cast(
                    HydroBreezeControlRequest.HydroBreezeMode, control.current_mode
                )
                self._attr_is_on = mode != HydroBreezeControlRequest.HydroBreezeMode.OFF
                self._attr_percentage = ordered_list_item_to_percentage(
                    list(HydroBreezeControlRequest.HydroBreezeMode), mode
                )
        self.async_write_ha_state()

    async def _async_set_mode(
        self, mode: HydroBreezeControlRequest.HydroBreezeMode
    ) -> None:
        await self.coordinator.api.async_set_value(
            device_id=self._device.device_id,
            control=HydroBreezeControlRequest(mode, self._control.zone_id),
        )
        if mode != HydroBreezeControlRequest.HydroBreezeMode.OFF:
            self._attr_percentage = get_percent(mode)
            self._attr_is_on = True
        else:
            self._attr_percentage = 0
            self._attr_is_on = False
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
