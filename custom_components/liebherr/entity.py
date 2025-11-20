"""Base Entityfor Liebherr appliances."""

from pyliebherr import LiebherrControl, LiebherrDevice

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .coordinator import LiebherrCoordinator


def async_get_unique_id(device_id: str, control_name: str, zone_id: int = 0) -> str:
    """Helper to form unique_id."""
    return f"{DOMAIN}_{device_id}_{control_name}_{zone_id}"


def async_get_device_info(device: LiebherrDevice) -> DeviceInfo:
    """Device Info Helper."""
    return {
        "identifiers": {(DOMAIN, device.device_id)},
        "name": device.name
        if device.name
        else f"Liebherr HomeAPI Appliance {device.device_id}",
        "manufacturer": "Liebherr",
        "model": device.model if device.model else "Unknown Model",
    }


class LiebherrEntity(Entity):
    """Representation of a Liebherr climate entity."""

    def __init__(
        self,
        coordinator: LiebherrCoordinator,
        device: LiebherrDevice,
        control: LiebherrControl,
    ) -> None:
        """Initialize the climate entity."""
        self._attr_has_entity_name = True
        self.coordinator: LiebherrCoordinator = coordinator
        self._device: LiebherrDevice = device
        self._control: LiebherrControl = control
        self._zone_id: int = control.zone_id
        self._attr_unique_id = async_get_unique_id(
            device.device_id, control.control_name, control.zone_id
        )
        self._attr_device_info = async_get_device_info(device)
        self._attr_translation_key = control.control_name
        if control.zone_position:
            self._attr_translation_placeholders = {
                "zone": f" {coordinator.zone_translations[f'component.{DOMAIN}.common.{control.zone_position}']}",
            }

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to register update signal handler."""
        self.async_on_remove(
            self._device.add_update_listener(self._handle_device_update)
        )

    def _handle_device_update(self) -> None:
        """Handle updated data from the device."""
        raise NotImplementedError("Must be implemented in subclass.")
