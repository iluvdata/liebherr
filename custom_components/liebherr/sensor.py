"""Last update sensor for Liebherr appliances."""

from datetime import UTC, datetime

from pyliebherr import CONTROL_TYPE, LiebherrControl, LiebherrDevice

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import LiebherrConfigEntry, LiebherrCoordinator
from .entity import LiebherrEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: LiebherrConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
):
    """Set up Liebherr appliances as devices and entities from a config entry."""

    devices: list[LiebherrDevice] = config_entry.runtime_data.data
    entities = []
    for device in devices:
        for control in device.controls:
            if control.type == CONTROL_TYPE.UPDATED:
                entities.append(  # noqa: PERF401
                    UpdateSensor(config_entry.runtime_data, device, control)
                )

    async_add_entities(entities, update_before_add=True)


class UpdateSensor(LiebherrEntity, SensorEntity):  # pyright: ignore[reportIncompatibleVariableOverride]
    """Representation of a Liebherr update sensor."""

    def __init__(
        self,
        coordinator: LiebherrCoordinator,
        device: LiebherrDevice,
        control: LiebherrControl,
    ) -> None:
        """Initialize the sensor entity."""
        super().__init__(coordinator, device, control)
        self._attr_icon = "mdi:clock-outline"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_entity_registry_enabled_default = False

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        for control in self._device.controls:
            if self._control.control_name == control.control_name:
                self._attr_native_value = datetime.now(UTC)
        self.async_write_ha_state()
