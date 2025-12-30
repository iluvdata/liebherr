"""Support for Liebherr HydroBreeze."""

import math
from typing import Any

from pyliebherr import LiebherrControl, LiebherrDevice
from pyliebherr.const import CONTROL_TYPE
from pyliebherr.models import PresentationLightControlRequest

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.util.color import brightness_to_value, value_to_brightness

from .const import BRIGHTNESS_SCALE, DEFAULT_BRIGHTNESS_SCALE
from .coordinator import LiebherrConfigEntry, LiebherrCoordinator
from .entity import LiebherrEntity


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
        self.brightness_scale: tuple[int, int] = BRIGHTNESS_SCALE.get(
            device.model, DEFAULT_BRIGHTNESS_SCALE
        )

    @property
    def available(self) -> bool:  # pyright: ignore[reportIncompatibleVariableOverride, reportIncompatibleMethodOverride]
        """Available."""
        return super().available

    def _handle_coordinator_update(self) -> None:
        for control in self._device.controls:
            if control.type == self._control.type:
                if control.target is not None and control.target > 0:
                    self._attr_brightness = value_to_brightness(
                        self.brightness_scale, control.target
                    )
                    self._attr_is_on = True
                else:
                    self._attr_is_on = False
        self.async_write_ha_state()

    async def async_turn_on(
        self,
        **kwargs: Any,
    ) -> None:
        """Turn the light on."""

        await self.coordinator.api.async_set_value(
            device_id=self._device.device_id,
            control=PresentationLightControlRequest(
                math.ceil(
                    brightness_to_value(self.brightness_scale, kwargs[ATTR_BRIGHTNESS])
                )
            ),
        )
        self._attr_brightness = kwargs[ATTR_BRIGHTNESS]
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        await self.coordinator.api.async_set_value(
            device_id=self._device.device_id,
            control=PresentationLightControlRequest(0),
        )
        self._attr_is_on = False
        self.async_write_ha_state()
