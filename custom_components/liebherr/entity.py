"""Base Entityfor Liebherr appliances."""

import logging
from typing import Any

from pyliebherr import (
    ControlType,
    LiebherrAPI,
    LiebherrControl,
    LiebherrControlKey,
    LiebherrControlRequest,
    LiebherrDevice,
)
from pyliebherr.exception import LiebherrSSEException

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import LiebherrConfigEntry
from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__name__)


def async_get_unique_id(
    device_id: str, control_name: str, zone_id: int | None = None
) -> str:
    """Helper to form unique_id."""
    return f"{DOMAIN}_{device_id}_{control_name}_{zone_id or 0}"


def async_get_device_info(device: LiebherrDevice) -> DeviceInfo:
    """Device Info Helper."""
    return DeviceInfo(
        identifiers={(DOMAIN, device.device_id)},
        name=device.name or f"Liebherr SmartDevice Appliance {device.device_id}",
        manufacturer="Liebherr",
        model=device.model or "Unknown Model",
        serial_number=device.device_id,
    )


class LiebherrEntity(Entity):
    """Representation of a Liebherr climate entity."""

    def __init__(
        self,
        config_entry: LiebherrConfigEntry,
        device: LiebherrDevice,
        control_key: LiebherrControlKey,
    ) -> None:
        """Initialize the entity."""
        self._attr_has_entity_name = True
        control: LiebherrControl = device.controls[control_key]
        device.controls[control_key].update_callback = self.async_write_ha_state
        self.api: LiebherrAPI = config_entry.runtime_data.api
        self.device: LiebherrDevice = device
        self.control_key: LiebherrControlKey = control_key
        self._attr_unique_id = async_get_unique_id(
            device.device_id, control.control_name, control.zone_id
        )
        self._attr_device_info = async_get_device_info(device)
        self._attr_translation_key = control.control_name
        if control.zone_position:
            self._attr_translation_placeholders = {
                "zone": f" {config_entry.runtime_data.translations[f'component.{DOMAIN}.common.{control.zone_position}']}",
            }

        def _error_callback(exc: LiebherrSSEException) -> None:
            """Wrapper function used to update the state to unavailable."""
            self.async_write_ha_state()

        device.add_error_callback(_error_callback)

    def available(self):
        """Available (SSE connected?)."""
        return self.device.available

    @property
    def control(self) -> LiebherrControl:
        """Get the control."""
        return self.device.controls[self.control_key]

    async def async_set_value(
        self, control: LiebherrControlRequest
    ) -> list[dict[str, Any]]:
        """Call api method for device via coordinator."""
        return await self.api.async_set_value(self.device.device_id, control)


async def base_async_setup_entry(
    config_entry: LiebherrConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
    liebherr_entity_class: type[LiebherrEntity],
    control_type: ControlType,
) -> None:
    """Set up Liebherr appliances as devices and entities from a config entry."""

    entities: list[LiebherrEntity] = []
    for device in config_entry.runtime_data.devices:
        if not device.controls:
            _LOGGER.warning("No controls found for device %s", device.device_id)
            continue
        if device.device_type in LiebherrDevice.DeviceType:
            for control in device.controls.values():
                if control.type == control_type:
                    entities.extend(
                        [
                            liebherr_entity_class(
                                config_entry,
                                device,
                                (control.control_name, control.zone_id),
                            )
                        ]
                    )
    async_add_entities(entities)
