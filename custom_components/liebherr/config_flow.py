"""Config flow for Liebherr Integration."""

from collections.abc import Mapping
from typing import Any

from pyliebherr import LiebherrAPI
from pyliebherr.exception import LiebherrAuthException
import voluptuous as vol

from homeassistant.config_entries import (
    SOURCE_REAUTH,
    SOURCE_USER,
    ConfigFlow,
    ConfigFlowResult,
)
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.selector import TextSelector

from . import _LOGGER
from .const import DOMAIN


class LiebherrConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Liebherr Integration."""

    VERSION = 1

    MINOR_VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # check the API key
            api: LiebherrAPI = LiebherrAPI(user_input[CONF_API_KEY])
            try:
                await api.async_get_appliances()
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
