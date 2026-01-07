"""Base Entityfor Liebherr appliances."""

import logging

from pyliebherr import LiebherrControl, LiebherrDevice
from pyliebherr.models import ControlType, LiebherrMappedControls

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LiebherrConfigEntry, LiebherrCoordinator

_LOGGER: logging.Logger = logging.getLogger(__name__)


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


class LiebherrEntity(CoordinatorEntity[LiebherrCoordinator]):
    """Representation of a Liebherr climate entity."""

    def __init__(
        self,
        coordinator: LiebherrCoordinator,
        device: LiebherrDevice,
        control: LiebherrControl,
    ) -> None:
        """Initialize the climate entity."""
        self._attr_has_entity_name = True
        super().__init__(coordinator)
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

    def get_control(self) -> LiebherrControl | None:
        """Get the current control from the device."""
        if controls := self._device.controls.get(self._control.type):
            if control := controls.get((self._zone_id, self._control.control_name)):
                return control
            _LOGGER.warning(
                "Control with zone ID %s not found for device %s and control type %s",
                self._zone_id,
                self._device.device_id,
                self._control.type,
            )
            return None
        _LOGGER.warning(
            "Control type %s not found for device %s",
            self._control.type,
            self._device.device_id,
        )
        return None


async def base_async_setup_entry(
    config_entry: LiebherrConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
    liebherr_entity_class: type[LiebherrEntity],
    control_type: ControlType,
) -> None:
    """Set up Liebherr appliances as devices and entities from a config entry."""

    devices: list[LiebherrDevice] = config_entry.runtime_data.data
    entities: list[LiebherrEntity] = []
    for device in devices:
        if not device.controls:
            _LOGGER.warning("No controls found for appliance %s", device.device_id)
            continue
        if device.type in LiebherrDevice.Type:
            controls: LiebherrMappedControls | None = device.controls.get(control_type)
            if controls is not None:
                entities = [
                    liebherr_entity_class(
                        coordinator=config_entry.runtime_data,
                        device=device,
                        control=control,
                    )
                    for control in controls.values()
                ]

    async_add_entities(entities)
