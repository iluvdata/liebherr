"""Support for Liebherr HydroBreeze."""

import math
from typing import Any

from pyliebherr import LiebherrControl, LiebherrDevice
from pyliebherr.const import ControlType
from pyliebherr.models import PresentationLightControlRequest

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.util.color import brightness_to_value, value_to_brightness

from .const import BRIGHTNESS_SCALE, DEFAULT_BRIGHTNESS_SCALE
from .coordinator import LiebherrConfigEntry, LiebherrCoordinator
from .entity import LiebherrEntity, base_async_setup_entry


async def async_setup_entry(
    hass: HomeAssistant, config_entry: LiebherrConfigEntry, async_add_entities
):
    """Set up Liebherr light from a config entry."""
    await base_async_setup_entry(
        config_entry, async_add_entities, LiebherrLight, ControlType.PRESENTATION_LIGHT
    )


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
        self._set_brightness()

    def _set_brightness(self) -> None:
        if self.control.target is not None and self.control.target > 0:
            self._attr_brightness = self._attr_brightness = value_to_brightness(
                self.brightness_scale, self.control.target
            )

    def _handle_coordinator_update(self) -> None:
        self.__handle_coordinator_update(False)
        self._set_brightness()
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool:
        """Light on attribute."""
        return self.control.target is not None and self.control.target > 0

    async def async_turn_on(
        self,
        **kwargs: Any,
    ) -> None:
        """Turn the light on."""

        # turn on via switch brightness not so will try to set to previous brightness
        # a brightness of zero won't turn on the light so turn on to max brightness
        brightness: int = (
            kwargs[ATTR_BRIGHTNESS]
            if kwargs[ATTR_BRIGHTNESS]
            else (self._attr_brightness if self._attr_brightness else 255)
        )

        self.control.target = math.ceil(
            brightness_to_value(self.brightness_scale, brightness)
        )
        await self.async_set_value(
            control=PresentationLightControlRequest(self.control.target),
        )

        self._attr_brightness = brightness
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        self.control.target = 0
        await self.async_set_value(
            control=PresentationLightControlRequest(0),
        )
        self.async_write_ha_state()
