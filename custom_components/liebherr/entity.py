"""Base Entityfor Liebherr appliances."""

import logging

from pyliebherr import LiebherrControl, LiebherrDevice
from pyliebherr.const import CONTROL_NAMES, ControlType

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LiebherrConfigEntry, LiebherrCoordinator

_LOGGER: logging.Logger = logging.getLogger(__name__)


def async_get_unique_id(
    device_id: str, control_name: str, zone_id: int | None = None
) -> str:
    """Helper to form unique_id."""
    return f"{DOMAIN}_{device_id}_{control_name}_{zone_id if zone_id else 0}"


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
        self._attr_unique_id = async_get_unique_id(
            device.device_id, control.control_name, control.zone_id
        )
        self._attr_device_info = async_get_device_info(device)
        self._attr_translation_key = control.control_name
        if control.zone_position:
            self._attr_translation_placeholders = {
                "zone": f" {coordinator.zone_translations[f'component.{DOMAIN}.common.{control.zone_position}']}",
            }

    @callback
    def __handle_coordinator_update(self, write: bool = True) -> None:
        """Get the current control from the device."""
        if controls := self._device.controls.get(self._control.control_name):
            if isinstance(controls, LiebherrControl):
                self._control = controls
                if write:
                    self.async_write_ha_state()
                return
            if control := controls.get(self._control.zone_id):
                self._control = control
                if write:
                    self.async_write_ha_state()
                return
            _LOGGER.warning(
                "Unable to find control %s for device %s with zone id %s",
                self._control.control_name,
                self._device.device_id,
                self._control.zone_id,
            )

    @callback
    def _handle_coordinator_update(self) -> None:
        self.__handle_coordinator_update()


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
        if device.deviceType in LiebherrDevice.DeviceType:
            for control_name in CONTROL_NAMES[control_type]:
                if controls := device.controls.get(control_name):
                    if isinstance(controls, LiebherrControl):
                        controls = {None: controls}
                    entities.extend(
                        [
                            liebherr_entity_class(
                                coordinator=config_entry.runtime_data,
                                device=device,
                                control=control,
                            )
                            for control in controls.values()
                        ]
                    )
    async_add_entities(entities)
