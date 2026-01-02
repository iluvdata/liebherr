"""Support for Liebherr mode selections."""

import logging

from pyliebherr import LiebherrControl, LiebherrDevice
from pyliebherr.const import CONTROL_TYPE
from pyliebherr.exception import LiebherrException
from pyliebherr.models import (
    BioFreshPlusControlRequest,
    IceMakerControlRequest,
    LiebherrControlRequest,
)

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant, callback

from .coordinator import LiebherrConfigEntry, LiebherrCoordinator
from .entity import LiebherrEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: LiebherrConfigEntry, async_add_entities
):
    """Set up Liebherr selects from a config entry."""

    entities = []

    for device in config_entry.runtime_data.data:
        controls: list[LiebherrControl] = device.controls
        if not controls:
            _LOGGER.warning("No controls found for appliance %s", device.device_id)
            continue

        for control in controls:
            if control.type in [CONTROL_TYPE.ICE_MAKER, CONTROL_TYPE.BIO_FRESH_PLUS]:
                entities.extend(
                    [LiebherrSelect(config_entry.runtime_data, device, control)]
                )

    async_add_entities(entities, update_before_add=True)


class LiebherrSelect(LiebherrEntity, SelectEntity):
    """Representation of a Liebherr select entity."""

    def __init__(
        self,
        coordinator: LiebherrCoordinator,
        device: LiebherrDevice,
        control: LiebherrControl,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator=coordinator, device=device, control=control)
        if control.type == CONTROL_TYPE.ICE_MAKER:
            self._attr_icon = "mdi:cube-outline"
            self._attr_options = (
                ["on", "off", "max_ice"] if control.hasMaxIce else ["on", "off"]
            )
        elif control.supportedModes is not None:
            self._attr_icon = "mdi: leaf"
            self._attr_options = [mode.lower() for mode in control.supportedModes]
        else:
            _LOGGER.error(
                "Cannot setup %s for device %s", control.type, device.device_id
            )

    @property
    def available(self) -> bool:  # pyright: ignore[reportIncompatibleVariableOverride]
        """Available from super."""
        return super().available

    @callback
    def _handle_coordinator_update(self) -> None:
        for control in self._device.controls:
            if (
                self._control.control_name == control.control_name
                and self._zone_id == control.zone_id
            ):
                if (
                    self._control.type == CONTROL_TYPE.ICE_MAKER
                    and control.iceMakerMode
                ):
                    self._attr_current_option = control.iceMakerMode.lower()
                elif control.current_mode:
                    self._attr_current_option = control.current_mode.lower()
                self._async_write_ha_state()
                return

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in self._attr_options:
            _LOGGER.error("Invalid option selected: %s", option)
            return

        data: LiebherrControlRequest
        try:
            if self._control.type == CONTROL_TYPE.ICE_MAKER:
                data = IceMakerControlRequest(
                    zoneId=self._control.zone_id,
                    iceMakerMode=IceMakerControlRequest.IceMakerMode(option.upper()),
                )
            else:
                data = BioFreshPlusControlRequest(
                    zoneId=self._control.zone_id,
                    bioFreshPlusMode=BioFreshPlusControlRequest.BioFreshPlusMode(
                        option.upper()
                    ),
                )

            await self.coordinator.api.async_set_value(
                self._device.device_id,
                data,
            )

            self._attr_current_option = option
            self._async_write_ha_state()

        except LiebherrException as e:
            _LOGGER.error(
                "Failed to set option '%s' for '%s': %s", option, self.unique_id, e
            )
            return
