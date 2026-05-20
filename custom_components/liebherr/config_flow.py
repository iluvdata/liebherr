"""Config flow for Liebherr Integration."""

from collections.abc import Mapping
import logging
import re
from typing import Any

from pyliebherr import LiebherrAPI
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
from homeassistant.helpers.selector import BooleanSelector, TextSelector

from . import LiebherrConfigEntry
from .const import (
    CONF_PRESENTATION_LIGHT_AS_NUMBER,
    DOMAIN,
    URL_CONNECT_INSTRUCTIONS,
    URL_DOWNLOAD_APP,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)

LIGHT_SECTION: str = "presentation_light_options"


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
                    CONF_PRESENTATION_LIGHT_AS_NUMBER: user_input[LIGHT_SECTION][
                        CONF_PRESENTATION_LIGHT_AS_NUMBER
                    ],
                }
            )
        suggested_values = {
            LIGHT_SECTION: {
                CONF_PRESENTATION_LIGHT_AS_NUMBER: self.config_entry.options.get(
                    CONF_PRESENTATION_LIGHT_AS_NUMBER, False
                ),
            },
        }
        OPTIONS_SCHEMA: vol.Schema = vol.Schema(
            {
                vol.Required(LIGHT_SECTION): section(
                    vol.Schema(
                        {
                            vol.Required(
                                CONF_PRESENTATION_LIGHT_AS_NUMBER
                            ): BooleanSelector(),
                        }
                    )
                ),
            }
        )
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA, suggested_values
            ),
            errors=errors,
        )


class LiebherrConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Liebherr Integration."""

    VERSION = 1

    MINOR_VERSION = 4

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # check the API key
            if not re.fullmatch("^\\S.*\\S$", user_input[CONF_API_KEY]):
                errors[CONF_API_KEY] = "whitespace_api_key"
            else:
                try:
                    api: LiebherrAPI = LiebherrAPI(user_input[CONF_API_KEY])
                    await api.async_test_key()
                except LiebherrAuthException:
                    errors["base"] = "auth_error"
                finally:
                    if hasattr(self, "api"):
                        await api.async_close()
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
            {vol.Required(CONF_API_KEY): vol.All(TextSelector())}
        )
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "url_download_app": URL_DOWNLOAD_APP,
                "url_connect_instructions": URL_CONNECT_INSTRUCTIONS,
            },
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
