"""Support for Liebherr mode selections."""

import logging

from pyliebherr import LiebherrControl
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
        control: LiebherrControl,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator=coordinator, control=control)

    @property
    def current_option(self) -> str | None:
        """Current Option."""
        return self.control.current_mode.lower() if self.control.current_mode else None

    async def _async_select_option(self, data: LiebherrControlRequest) -> None:
        try:
            await self.async_set_value(
                data,
            )

        except LiebherrException as e:
            _LOGGER.error(
                "Failed to set option '%s' for '%s': %s",
                data,
                self.coordinator.device.device_id,
                e,
            )


class LiebherrBioFreshPlus(LiebherrSelect):
    """Representation of a Liebherr select entity."""

    def __init__(
        self,
        coordinator: LiebherrCoordinator,
        control: LiebherrControl,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator=coordinator, control=control)
        self._attr_icon = "mdi: leaf"
        if control.supported_modes is not None:
            self._attr_options = [mode.lower() for mode in control.supported_modes]
        else:
            _LOGGER.error(
                "Cannot setup %s for device %s",
                control.type,
                coordinator.device.device_id,
            )

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in self._attr_options:
            _LOGGER.error("Invalid option selected: %s", option)
            return

        data: LiebherrControlRequest = BioFreshPlusControlRequest(
            zone_id=self.control.zone_id or 0,
            bio_fresh_plus_mode=BioFreshPlusControlRequest.BioFreshPlusMode(
                option.upper()
            ),
        )
        await self._async_select_option(data)

        self.control.current_mode = option
        self.async_write_ha_state()


class LiebherrIceMaker(LiebherrSelect):
    """Select entity representing an IceMaker."""

    def __init__(
        self,
        coordinator: LiebherrCoordinator,
        control: LiebherrControl,
    ) -> None:
        """Initialize the Ice Maker entity."""
        super().__init__(coordinator=coordinator, control=control)
        self._attr_icon = "mdi:cube-outline"
        self._attr_options = (
            ["on", "off", "max_ice"] if control.has_max_ice else ["on", "off"]
        )

    @property
    def current_option(self) -> str | None:
        """Current option."""
        return (
            self.control.ice_maker_mode.lower() if self.control.ice_maker_mode else None
        )

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in self._attr_options:
            _LOGGER.error("Invalid option selected: %s", option)
            return

        data: LiebherrControlRequest = IceMakerControlRequest(
            zone_id=self.control.zone_id or 0,
            ice_maker_mode=IceMakerControlRequest.IceMakerMode(option.upper()),
        )

        await self._async_select_option(data)
        self.control.ice_maker_mode = IceMakerControlRequest.IceMakerMode(
            option.upper()
        )
        self._async_write_ha_state()
