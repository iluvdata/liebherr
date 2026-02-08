"""Last update sensor for Liebherr appliances."""

from dataclasses import dataclass
from datetime import UTC, datetime

from pyliebherr import ControlType, LiebherrControl

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import LiebherrConfigEntry, LiebherrCoordinator
from .entity import LiebherrEntity


@dataclass
class LiebherrUpdateControl(LiebherrControl):
    """Overrride LiebherrControl."""

    _control_name: str = "updated"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: LiebherrConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
):
    """Set up Liebherr appliances as devices and entities from a config entry."""

    async_add_entities(
        [
            UpdateSensor(
                coordinator,
                LiebherrUpdateControl(ControlType.UPDATED),
            )
            for coordinator in config_entry.runtime_data.coordinators
        ]
    )


class UpdateSensor(LiebherrEntity, SensorEntity):  # pyright: ignore[reportIncompatibleVariableOverride]
    """Representation of a Liebherr update sensor."""

    def __init__(
        self,
        coordinator: LiebherrCoordinator,
        control: LiebherrControl,
    ) -> None:
        """Initialize the sensor entity."""
        super().__init__(coordinator, control)
        self._attr_icon = "mdi:clock-outline"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_entity_registry_enabled_default = False
        self._attr_native_value = datetime.now(UTC)

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = datetime.now(UTC)
        self.async_write_ha_state()
