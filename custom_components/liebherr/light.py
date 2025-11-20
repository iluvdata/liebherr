"""Support for Liebherr HydroBreeze."""

import logging
from typing import Any

from pyliebherr import LiebherrControl, LiebherrDevice
from pyliebherr.const import CONTROL_TYPE
from pyliebherr.models import PresentationLightControlRequest

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.util.color import value_to_brightness

from .coordinator import LiebherrConfigEntry, LiebherrCoordinator
from .entity import LiebherrEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: LiebherrConfigEntry, async_add_entities
):
    """Set up Liebherr switches from a config entry."""
    entities: list[LiebherrLight] = []
    for device in config_entry.runtime_data.data:
        for control in device.controls:
            if control.type == CONTROL_TYPE.PRESENTATION_LIGHT:
                entities.extend(
                    [LiebherrLight(config_entry.runtime_data, device, control)]
                )
    async_add_entities(entities, update_before_add=True)


BRIGHTNESS_SCALE = (1, 4)


class LiebherrLight(LiebherrEntity, LightEntity):
    """Representation of a Liebherr switch entity."""

    def __init__(
        self,
        coordinator: LiebherrCoordinator,
        device: LiebherrDevice,
        control: LiebherrControl,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator, device, control)
        self._attr_icon = "mdi:lightbulb"
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    @property
    def available(self) -> bool:  # pyright: ignore[reportIncompatibleVariableOverride, reportIncompatibleMethodOverride]
        """Available."""
        return super().available

    def _handle_device_update(self) -> None:
        for control in self._device.controls:
            if control.type == self._control.type:
                if control.target is not None:
                    self._attr_brightness = value_to_brightness(
                        BRIGHTNESS_SCALE, control.target
                    )
                    self._attr_is_on = control.target > 0
        self.async_write_ha_state()

    async def _async_on_off(self, brightness: int) -> None:
        await self.coordinator.api.async_set_value(
            device_id=self._device.device_id,
            control=PresentationLightControlRequest(brightness),
        )
        if brightness > 0:
            self._attr_brightness = value_to_brightness(BRIGHTNESS_SCALE, brightness)
            self._attr_is_on = True
        else:
            self._attr_is_on = False

        self.async_write_ha_state()

    async def async_turn_on(
        self,
        **kwargs: Any,
    ) -> None:
        """Turn the light on."""
        await self._async_on_off(
            value_to_brightness(BRIGHTNESS_SCALE, kwargs[ATTR_BRIGHTNESS])
        )

    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        await self._async_on_off(0)
