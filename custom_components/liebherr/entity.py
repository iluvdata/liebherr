"""Base Entityfor Liebherr appliances."""

from pyliebherr import LiebherrControl, LiebherrDevice

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LiebherrCoordinator


class LiebherrEntity(CoordinatorEntity[LiebherrCoordinator]):
    """Representation of a Liebherr climate entity."""

    def __init__(
        self,
        coordinator: LiebherrCoordinator,
        device: LiebherrDevice,
        control: LiebherrControl,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator=coordinator)
        self._attr_has_entity_name = True
        self._device: LiebherrDevice = device
        self._control: LiebherrControl = control
        self._zone_id: int = control.zone_id
        # self._attr_name = f"{control.control_name.capitalize()}"
        # if control.zone_position:
        #    self._attr_name = f"{self._attr_name} {control.zone_position.capitalize()}"
        self._attr_unique_id = (
            f"liebherr_{device.device_id}_{control.control_name}_{self._zone_id}"
        )
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.device_id)},
            "name": device.name
            if device.name
            else f"Liebherr HomeAPI Appliance {device.device_id}",
            "manufacturer": "Liebherr",
            "model": device.model if device.model else "Unknown Model",
        }
        self.translation_key = control.control_name
        self.translation_placeholders = {
            "zone": (
                f" {control.zone_position.capitalize()}"
                if control.zone_position
                else "Test"
            ),
        }
