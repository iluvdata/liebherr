"""Support for Liebherr mode selections."""

import logging

from pyliebherr import LiebherrControl, LiebherrDevice
from pyliebherr.const import ControlType
from pyliebherr.exception import LiebherrException
from pyliebherr.models import (
    BioFreshPlusControlRequest,
    IceMakerControlRequest,
    LiebherrControlRequest,
)

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant

from .coordinator import LiebherrConfigEntry, LiebherrCoordinator
from .entity import LiebherrEntity, base_async_setup_entry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: LiebherrConfigEntry, async_add_entities
):
    """Set up Liebherr selects from a config entry."""

    await base_async_setup_entry(
        config_entry,
        async_add_entities,
        LiebherrBioFreshPlus,
        ControlType.BIO_FRESH_PLUS,
    )

    await base_async_setup_entry(
        config_entry, async_add_entities, LiebherrIceMaker, ControlType.ICE_MAKER
    )


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

    @property
    def current_option(self) -> str | None:
        """Current Option."""
        return (
            self._control.current_mode.lower() if self._control.current_mode else None
        )

    async def _async_select_option(self, data: LiebherrControlRequest) -> None:
        try:
            await self.coordinator.api.async_set_value(
                self._device.device_id,
                data,
            )

        except LiebherrException as e:
            _LOGGER.error(
                "Failed to set option '%s' for '%s': %s",
                data,
                self._device.device_id,
                e,
            )


class LiebherrBioFreshPlus(LiebherrSelect):
    """Representation of a Liebherr select entity."""

    def __init__(
        self,
        coordinator: LiebherrCoordinator,
        device: LiebherrDevice,
        control: LiebherrControl,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator=coordinator, device=device, control=control)
        self._attr_icon = "mdi: leaf"
        if control.supportedModes is not None:
            self._attr_options = [mode.lower() for mode in control.supportedModes]
        else:
            _LOGGER.error(
                "Cannot setup %s for device %s", control.type, device.device_id
            )

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in self._attr_options:
            _LOGGER.error("Invalid option selected: %s", option)
            return

        data: LiebherrControlRequest = BioFreshPlusControlRequest(
            zoneId=self._control.zone_id if self._control.zone_id else 0,
            bioFreshPlusMode=BioFreshPlusControlRequest.BioFreshPlusMode(
                option.upper()
            ),
        )
        await self._async_select_option(data)

        self._control.currentMode = option
        self.async_write_ha_state()


class LiebherrIceMaker(LiebherrSelect):
    """Select entity representing an IceMaker."""

    def __init__(
        self,
        coordinator: LiebherrCoordinator,
        device: LiebherrDevice,
        control: LiebherrControl,
    ) -> None:
        """Initialize the Ice Maker entity."""
        super().__init__(coordinator=coordinator, device=device, control=control)
        self._attr_icon = "mdi:cube-outline"
        self._attr_options = (
            ["on", "off", "max_ice"] if control.hasMaxIce else ["on", "off"]
        )

    @property
    def current_option(self) -> str | None:
        """Current option."""
        return (
            self._control.iceMakerMode.lower() if self._control.iceMakerMode else None
        )

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in self._attr_options:
            _LOGGER.error("Invalid option selected: %s", option)
            return

        data: LiebherrControlRequest = IceMakerControlRequest(
            zoneId=self._control.zone_id if self._control.zone_id else 0,
            iceMakerMode=IceMakerControlRequest.IceMakerMode(option.upper()),
        )

        await self._async_select_option(data)
        self._control.iceMakerMode = IceMakerControlRequest.IceMakerMode(option.upper())
        self._async_write_ha_state()
