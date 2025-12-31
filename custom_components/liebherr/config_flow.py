"""Config flow for Liebherr Integration."""

from collections.abc import Mapping
from typing import Any

from pyliebherr import LiebherrAPI, LiebherrDevice
from pyliebherr.exception import LiebherrAuthException
import voluptuous as vol

from homeassistant.config_entries import (
    SOURCE_REAUTH,
    SOURCE_USER,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.const import CONF_API_KEY
from homeassistant.core import callback
from homeassistant.data_entry_flow import section
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
)

from . import _LOGGER
from .const import (
    CONF_POLL_INTERVAL,
    CONF_PRESENTATION_LIGHT_AS_SELECT,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    MAX_UPDATE_INTERVAL,
    MIN_UPDATE_INTERVAL,
)
from .coordinator import LiebherrConfigEntry

POLLING_SECTION: str = "polling_options"
LIGHT_SECTION: str = "presentation_light_options"

OPTIONS_SCHEMA: vol.Schema = vol.Schema(
    {
        vol.Required(POLLING_SECTION): section(
            vol.Schema(
                {
                    vol.Required(CONF_POLL_INTERVAL): NumberSelector(
                        NumberSelectorConfig(
                            min=MIN_UPDATE_INTERVAL,
                            max=MAX_UPDATE_INTERVAL,  # 5 minutes
                            step=1,
                            unit_of_measurement="s",
                            mode=NumberSelectorMode.BOX,
                        )
                    )
                }
            )
        ),
        vol.Required(LIGHT_SECTION): section(
            vol.Schema(
                {
                    vol.Required(CONF_PRESENTATION_LIGHT_AS_SELECT): BooleanSelector(),
                }
            )
        ),
    }
)


def async_calculate_poll_interval(number_of_devices: int) -> int:
    """Calculate poll interval based on number of devices."""
    if number_of_devices == 1:
        return DEFAULT_UPDATE_INTERVAL
    return max(
        # this ensures that the controls for eac device aren't polled more frequently than
        # the recommended default interval.
        round(DEFAULT_UPDATE_INTERVAL / number_of_devices),
        MIN_UPDATE_INTERVAL,
    )


class OptionsFlowHandler(OptionsFlowWithReload):
    """Handle options flow for Liebherr Integration."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}
        if user_input is not None:
            return self.async_create_entry(
                data={
                    CONF_POLL_INTERVAL: user_input[POLLING_SECTION][CONF_POLL_INTERVAL],
                    CONF_PRESENTATION_LIGHT_AS_SELECT: user_input[LIGHT_SECTION][
                        CONF_PRESENTATION_LIGHT_AS_SELECT
                    ],
                }
            )

        data_schema: vol.Schema = vol.Schema(
            {
                vol.Required("polling_options"): section(
                    vol.Schema(
                        {
                            vol.Required(CONF_POLL_INTERVAL): NumberSelector(
                                NumberSelectorConfig(
                                    min=MIN_UPDATE_INTERVAL,
                                    max=MAX_UPDATE_INTERVAL,  # 5 minutes
                                    step=1,
                                    unit_of_measurement="s",
                                    mode=NumberSelectorMode.BOX,
                                )
                            )
                        }
                    )
                ),
                vol.Required("presentation_light_options"): section(
                    vol.Schema(
                        {
                            vol.Required(
                                CONF_PRESENTATION_LIGHT_AS_SELECT
                            ): BooleanSelector(),
                        }
                    )
                ),
            }
        )
        suggested_values = {
            "polling_options": {
                CONF_POLL_INTERVAL: self.config_entry.options.get(
                    CONF_POLL_INTERVAL,
                    async_calculate_poll_interval(
                        len(self.config_entry.runtime_data.data)
                    ),
                )
            },
            "presentation_light_options": {
                CONF_PRESENTATION_LIGHT_AS_SELECT: self.config_entry.options.get(
                    CONF_PRESENTATION_LIGHT_AS_SELECT, False
                ),
            },
        }
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                data_schema, suggested_values
            ),
            description_placeholders={
                "min_int": str(MIN_UPDATE_INTERVAL),
                "max_int": str(MAX_UPDATE_INTERVAL),
                "rec_int": str(
                    async_calculate_poll_interval(
                        len(self.config_entry.runtime_data.data)
                    )
                ),
            },
            errors=errors,
        )


class LiebherrConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Liebherr Integration."""

    VERSION = 1

    MINOR_VERSION = 3

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # check the API key
            api: LiebherrAPI = LiebherrAPI(user_input[CONF_API_KEY])
            devices: list[LiebherrDevice] = []
            try:
                devices = await api.async_get_appliances()
            except LiebherrAuthException:
                errors["base"] = "auth_error"
            if not errors:
                await self.async_set_unique_id(f"{DOMAIN}_{user_input[CONF_API_KEY]}")
                self._abort_if_unique_id_configured()
                if self.source == SOURCE_USER:
                    return self.async_create_entry(
                        title="Liebherr SmartDevice",
                        data={
                            CONF_API_KEY: user_input[CONF_API_KEY],
                        },
                        options={
                            CONF_POLL_INTERVAL: async_calculate_poll_interval(
                                len(devices)
                            ),
                        },
                    )
                if self.source == SOURCE_REAUTH:
                    return self.async_update_reload_and_abort(
                        self._get_reauth_entry(),
                        unique_id=f"{DOMAIN}_{user_input[CONF_API_KEY]}",
                        data={
                            CONF_API_KEY: user_input[CONF_API_KEY],
                        },
                    )
                _LOGGER.error(
                    "An invalid config flow source was specified: %s", self.source
                )
                return self.async_abort(reason="invalid_source")

        data_schema: vol.Schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): TextSelector(),
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Perform reauth upon an API authentication error."""
        return await self.async_step_user()

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: LiebherrConfigEntry,
    ) -> OptionsFlowHandler:
        """Create the options flow."""
        return OptionsFlowHandler()
