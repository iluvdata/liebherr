"""Config flow for Liebherr Integration."""

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.selector import TextSelector

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
            return self.async_create_entry(
                title="Liebherr SmartDevice",
                data={
                    CONF_API_KEY: user_input[CONF_API_KEY],
                },
            )

        data_schema: vol.Schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): TextSelector(),
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
