"""Support for Liebherr mode switches."""

import logging
from typing import Any, Final

from pyliebherr import LiebherrControl, LiebherrDevice
from pyliebherr.const import CONTROL_TYPE
from pyliebherr.models import BaseToggleControlRequest, ZoneToggleControlRequest

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import ATTR_ICON
from homeassistant.core import HomeAssistant

from .coordinator import LiebherrConfigEntry, LiebherrCoordinator
from .entity import LiebherrEntity

_LOGGER = logging.getLogger(__name__)

CONFIG: Final[dict[str, dict[str, Any]]] = {
    "supercool": {ATTR_ICON: "mdi:snowflake", "zone": True},
    "superfrost": {
        ATTR_ICON: "mdi:snowflake-variant",
        "zone": True,
    },
    "partymode": {
        ATTR_ICON: "mdi:party-popper",
    },
    "nightmode": {
        ATTR_ICON: "mdi:weather-night",
    },
}


async def async_setup_entry(
    hass: HomeAssistant, config_entry: LiebherrConfigEntry, async_add_entities
):
    """Set up Liebherr switches from a config entry."""

    entities = []
    for device in config_entry.runtime_data.data:
        controls: list[LiebherrControl] = device.controls
        if not controls:
            _LOGGER.warning("No controls found for appliance %s", device.device_id)
            continue

        for control in controls:
            if control.type == CONTROL_TYPE.TOGGLE:
                entities.extend(
                    [
                        LiebherrSwitch(config_entry.runtime_data, device, control),
                    ]
                )

    if not entities:
        _LOGGER.error("No switch entities created")

    async_add_entities(entities, update_before_add=True)


class LiebherrSwitch(LiebherrEntity, SwitchEntity):  # pyright: ignore[reportIncompatibleVariableOverride]
    """Representation of a Liebherr switch entity."""

    def __init__(
        self,
        coordinator: LiebherrCoordinator,
        device: LiebherrDevice,
        control: LiebherrControl,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator, device, control)
        self._attr_icon = CONFIG.get(self._control.control_name.lower(), {}).get(
            ATTR_ICON, "mdi:toggle-switch-variant"
        )

    def _handle_coordinator_update(self) -> None:
        for control in self._device.controls:
            if (
                control.control_name == self._control.control_name
                and control.zone_id == self._control.zone_id
            ):
                self._attr_is_on = (
                    control.value
                    if isinstance(control.value, bool)
                    else bool(control.value)
                )
        self.async_write_ha_state()

    async def _async_set_toggle(self, turn_on: bool) -> None:
        control_name = self._control.control_name.lower()
        if not (config := CONFIG.get(control_name, {})):
            _LOGGER.error(
                "Could not map set request for %s using control_name %s",
                self._device.device_id,
                control_name,
            )
            return

        controlrequest: BaseToggleControlRequest | ZoneToggleControlRequest = (
            BaseToggleControlRequest(value=turn_on)
            if "zone" not in config
            else ZoneToggleControlRequest(value=turn_on, zoneId=self._control.zone_id)
        )
        controlrequest.control_name = self._control.control_name
        await self.coordinator.api.async_set_value(
            device_id=self._device.device_id,
            control=controlrequest,
        )
        self._attr_is_on = turn_on
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        await self._async_set_toggle(True)

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self._async_set_toggle(False)
