"""Support for Liebherr mode switches."""

import logging
from typing import Any, Final

from pyliebherr import LiebherrControl
from pyliebherr.const import ControlType
from pyliebherr.models import BaseToggleControlRequest, ZoneToggleControlRequest

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import ATTR_ICON
from homeassistant.core import HomeAssistant

from .coordinator import LiebherrConfigEntry, LiebherrCoordinator
from .entity import LiebherrEntity, base_async_setup_entry

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

    await base_async_setup_entry(
        config_entry, async_add_entities, LiebherrSwitch, ControlType.TOGGLE
    )


class LiebherrSwitch(LiebherrEntity, SwitchEntity):  # pyright: ignore[reportIncompatibleVariableOverride]
    """Representation of a Liebherr switch entity."""

    def __init__(
        self,
        coordinator: LiebherrCoordinator,
        control: LiebherrControl,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator, control)
        self._attr_icon = CONFIG.get(self.control.control_name.lower(), {}).get(
            ATTR_ICON, "mdi:toggle-switch-variant"
        )

    @property
    def is_on(self) -> bool:
        """Is on attribute."""
        return (
            self.control.value
            if isinstance(self.control.value, bool)
            else bool(self.control.value)
        )

    async def _async_set_toggle(self, turn_on: bool) -> None:
        control_name = self.control.control_name.lower()
        if not (config := CONFIG.get(control_name, {})):
            _LOGGER.error(
                "Could not map set request for %s using control_name %s",
                self.coordinator.device.device_id,
                control_name,
            )
            return

        controlrequest: BaseToggleControlRequest | ZoneToggleControlRequest = (
            BaseToggleControlRequest(value=turn_on)
            if "zone" not in config
            else ZoneToggleControlRequest(
                value=turn_on,
                zone_id=self.control.zone_id if self.control.zone_id is not None else 0,
            )
        )
        controlrequest.control_name = self.control.control_name
        await self.async_set_value(
            control=controlrequest,
        )
        self.control.value = turn_on
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        await self._async_set_toggle(True)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        await self._async_set_toggle(False)
