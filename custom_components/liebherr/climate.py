"""Support for Liebherr appliances as climate devices."""

from pyliebherr import LiebherrControl, LiebherrDevice
from pyliebherr.const import ControlType, ZonePosition
from pyliebherr.models import TemperatureControlRequest

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import LiebherrConfigEntry, LiebherrCoordinator
from .entity import LiebherrEntity, base_async_setup_entry


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: LiebherrConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
):
    """Set up Liebherr appliances as devices and entities from a config entry."""

    await base_async_setup_entry(
        config_entry, async_add_entities, LiebherrClimate, ControlType.TEMPERATURE
    )


class LiebherrClimate(LiebherrEntity, ClimateEntity):
    """Representation of a Liebherr climate entity."""

    def __init__(
        self,
        coordinator: LiebherrCoordinator,
        control: LiebherrControl,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator=coordinator, control=control)
        self._attr_target_temperature_step = 1
        self._attr_temperature_unit = (
            control.unit_of_measurement
            if control.unit_of_measurement is not None
            else "°C"
        )
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        self._attr_hvac_modes = [HVACMode.COOL]
        self._attr_hvac_mode = HVACMode.COOL
        if self.coordinator.device.device_type != LiebherrDevice.DeviceType.COMBI:
            self._attr_icon = "mdi:fridge-industrial-outline"
        elif control.zone_position == ZonePosition.TOP:
            self._attr_icon = "mdi:fridge-top"
        elif control.zone_position == ZonePosition.BOTTOM:
            self._attr_icon = "mdi:fridge-bottom"
        else:
            self._attr_icon = "mdi:fridge"
        if (
            control.min
            and control.max
            and control.unit_of_measurement
            and (
                (control.unit_of_measurement == "°F" and control.min < 0 < control.max)
                or (
                    control.unit_of_measurement == "°C"
                    and control.min < -17 < control.max
                )
            )
        ):
            # we have a freezer
            self._attr_translation_key = "freezer"
        else:
            self._attr_translation_key = "fridge"

    async def async_set_temperature(self, **kwargs):
        """Set the target temperature."""
        if ATTR_TEMPERATURE in kwargs:
            temperature: int = kwargs[ATTR_TEMPERATURE]

            data = TemperatureControlRequest(
                zone_id=self.control.zone_id or 0,
                target=temperature,
                unit=self._attr_temperature_unit,
            )

            await self.async_set_value(data)
            self.control.target = temperature
            self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode):
        """Set the HVAC mode."""
        if hvac_mode in self._attr_hvac_modes:
            self._attr_hvac_mode = hvac_mode

    @property
    def target_temperature(self) -> float | None:
        """Target Temperature."""
        return self.control.target

    @property
    def min_temp(self) -> float | None:
        """Min Temp."""
        return self.control.min

    @property
    def max_temp(self) -> float | None:
        """Max Temp."""
        return self.control.max

    @property
    def current_temperature(self) -> float | None:
        """Current Temp."""
        return self.control.value if isinstance(self.control.value, int) else None
