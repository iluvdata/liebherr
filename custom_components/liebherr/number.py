"""Number entity definitions for Liebherr integration."""

from pyliebherr import LiebherrControl, LiebherrDevice
from pyliebherr.const import ControlType
from pyliebherr.exception import LiebherrException
from pyliebherr.models import PresentationLightControlRequest

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import BRIGHTNESS_SCALE, DEFAULT_BRIGHTNESS_SCALE
from .coordinator import LiebherrConfigEntry, LiebherrCoordinator
from .entity import LiebherrEntity, base_async_setup_entry


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: LiebherrConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
):
    """Set up Liebherr number entities from a config entry."""

    await base_async_setup_entry(
        config_entry, async_add_entities, LiebherrNumber, ControlType.PRESENTATION_LIGHT
    )


class LiebherrNumber(LiebherrEntity, NumberEntity):
    """Representation of a Liebherr number entity."""

    def __init__(
        self,
        coordinator: LiebherrCoordinator,
        device: LiebherrDevice,
        control: LiebherrControl,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, device, control)
        self._attr_icon = "mdi:lightbulb"
        self.brightness_scale: tuple[int, int] = BRIGHTNESS_SCALE.get(
            device.model, DEFAULT_BRIGHTNESS_SCALE
        )
        self._attr_native_min_value = 0
        self._attr_native_max_value = self.brightness_scale[1]
        self._attr_native_step = 1
        self._attr_mode = NumberMode.SLIDER

    @property
    async def native_value(self) -> float:
        """Light brightness."""
        return (
            self._control.target
            if self._control.target is not None and self._control.target > 0
            else 0
        )

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        try:
            await self.coordinator.api.async_set_value(
                device_id=self._device.device_id,
                control=PresentationLightControlRequest(int(value)),
            )
        except LiebherrException as ex:
            raise HomeAssistantError(f"Error setting value: {value}") from ex

        self._control.target = round(value)
        self.async_write_ha_state()
