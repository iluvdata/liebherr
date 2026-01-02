"""Number entity definitions for Liebherr integration."""

from pyliebherr import LiebherrControl, LiebherrDevice
from pyliebherr.const import CONTROL_TYPE
from pyliebherr.exception import LiebherrException
from pyliebherr.models import PresentationLightControlRequest

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import BRIGHTNESS_SCALE, DEFAULT_BRIGHTNESS_SCALE
from .coordinator import LiebherrConfigEntry, LiebherrCoordinator
from .entity import LiebherrEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: LiebherrConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
):
    """Set up Liebherr number entities from a config entry."""

    entities: list[LiebherrNumber] = []

    for device in config_entry.runtime_data.data:
        for control in device.controls:
            if control.type == CONTROL_TYPE.PRESENTATION_LIGHT:
                entities.extend(
                    [LiebherrNumber(config_entry.runtime_data, device, control)]
                )
                break  # inner loop

    async_add_entities(entities)


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
    def available(self) -> bool:  # pyright: ignore[reportIncompatibleVariableOverride, reportIncompatibleMethodOverride]
        """Available."""
        return super().available

    def _handle_coordinator_update(self) -> None:
        for control in self._device.controls:
            if control.type == self._control.type:
                if control.target is not None and control.target > 0:
                    self._attr_native_value = control.target
                else:
                    self._attr_native_value = 0
                self.async_write_ha_state()
                return

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""

        try:
            await self.coordinator.api.async_set_value(
                device_id=self._device.device_id,
                control=PresentationLightControlRequest(int(value)),
            )
        except LiebherrException as ex:
            raise HomeAssistantError(f"Error setting value: {value}") from ex
