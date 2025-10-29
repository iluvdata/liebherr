"""Support for Liebherr appliances as climate devices."""

from asyncio import sleep
import logging

from pyliebherr import LiebherrControl, LiebherrDevice
from pyliebherr.const import CONTROL_TYPE
from pyliebherr.models import TemperatureControlRequest

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import LiebherrConfigEntry, LiebherrCoordinator
from .entity import LiebherrEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: LiebherrConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
):
    """Set up Liebherr appliances as devices and entities from a config entry."""

    devices: list[LiebherrDevice] = config_entry.runtime_data.data
    entities = []
    for device in devices:
        if not device.controls:
            _LOGGER.warning("No controls found for appliance %s", device.device_id)
            continue
        if device.type in LiebherrDevice.Type:
            for control in device.controls:
                if control.type == CONTROL_TYPE.TEMPERATURE:
                    _LOGGER.debug(
                        "Adding climate entity for %s_%s_%s",
                        device.device_id,
                        control.control_name if control.control_name else control.type,
                        control.zone_position,
                    )
                    entities.append(
                        LiebherrClimate(config_entry.runtime_data, device, control)
                    )

    async_add_entities(entities, update_before_add=True)


class LiebherrClimate(LiebherrEntity, ClimateEntity):
    """Representation of a Liebherr climate entity."""

    def __init__(
        self,
        coordinator: LiebherrCoordinator,
        device: LiebherrDevice,
        control: LiebherrControl,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator=coordinator, device=device, control=control)
        self._attr_target_temperature_step = 1
        self._attr_temperature_unit = (
            control.unit_of_measurement
            if control.unit_of_measurement is not None
            else ""
        )
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        self._attr_hvac_modes = [HVACMode.COOL]
        self._attr_hvac_mode = HVACMode.COOL
        self._attr_icon = "mdi:fridge"

    @property
    def available(self) -> bool:  # pyright: ignore[reportIncompatibleVariableOverride, reportIncompatibleMethodOverride]
        """Available."""
        return super().available

    async def async_set_temperature(self, **kwargs):
        """Set the target temperature."""
        if ATTR_TEMPERATURE in kwargs:
            temperature = kwargs[ATTR_TEMPERATURE]

            self._attr_target_temperature = temperature
            self.async_write_ha_state()

            data = TemperatureControlRequest(
                zoneId=self._zone_id,
                target=temperature,
                unit=self._attr_temperature_unit,
            )

            await self.coordinator.api.async_set_value(self._device.device_id, data)
            await sleep(5)
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode):
        """Set the HVAC mode."""
        if hvac_mode in self._attr_hvac_modes:
            self._attr_hvac_mode = hvac_mode

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        for control in self._device.controls:
            if self._control.control_name == control.control_name:
                if self._zone_id == control.zone_id:
                    self._attr_target_temperature = control.target
                    self._attr_current_temperature = control.value
                    if control.min:
                        self._attr_min_temp = control.min
                    if control.max:
                        self._attr_max_temp = control.max
        self.async_write_ha_state()
