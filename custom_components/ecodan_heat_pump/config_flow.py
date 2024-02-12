"""Adds config flow for Blueprint."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_ACCESS_TOKEN
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    ApiClient,
    ApiClientAuthenticationError,
    ApiClientCommunicationError,
    ApiClientError,
)
from .const import DOMAIN, LOGGER

USERNAME_1 = "username_1"
USERNAME_2 = "username_2"
USERNAME_3 = "username_3"

PASSWORD_1 = "password_1"
PASSWORD_2 = "password_2"
PASSWORD_3 = "password_3"


class ConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for integration"""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            LOGGER.debug("Testing user input...")
            try:
                await self._test_credentials(
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
            except ApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except ApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except ApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="init",
            data_schema={
                vol.Required(USERNAME_1): TextSelector(
                    TextSelectorConfig(
                        type=TextSelectorType.TEXT, autocomplete="username"
                    )
                ),
                vol.Required(PASSWORD_1): TextSelector(
                    TextSelectorConfig(
                        type=TextSelectorType.TEXT, autocomplete="password"
                    )
                ),
                vol.Optional(USERNAME_2): TextSelector(
                    TextSelectorConfig(
                        type=TextSelectorType.TEXT, autocomplete="username"
                    )
                ),
                vol.Optional(PASSWORD_2): TextSelector(
                    TextSelectorConfig(
                        type=TextSelectorType.TEXT, autocomplete="password"
                    )
                ),
                vol.Optional(USERNAME_3): TextSelector(
                    TextSelectorConfig(
                        type=TextSelectorType.TEXT, autocomplete="username"
                    )
                ),
                vol.Optional(PASSWORD_3): TextSelector(
                    TextSelectorConfig(
                        type=TextSelectorType.TEXT, autocomplete="password"
                    )
                ),
            },
            # data_schema=vol.Schema(
            #     {
            #         vol.Required(
            #             CONF_USERNAME,
            #             default=(user_input or {}).get(CONF_USERNAME),
            #         ): selector.TextSelector(
            #             selector.TextSelectorConfig(
            #                 type=selector.TextSelectorType.TEXT
            #             ),
            #         ),
            #         vol.Required(CONF_PASSWORD): selector.TextSelector(
            #             selector.TextSelectorConfig(
            #                 type=selector.TextSelectorType.PASSWORD
            #             ),
            #         ),
            #         vol.Required(
            #             CONF_ACCESS_TOKEN,
            #             default=(user_input or {}).get(CONF_ACCESS_TOKEN),
            #         ): selector.TextSelector(
            #             selector.TextSelectorConfig(
            #                 type=selector.TextSelectorType.TEXT
            #             ),
            #         ),
            #     }
            # ),
            errors=_errors,
        )

    async def _test_credentials(self, username: str, password: str) -> None:
        """Validate credentials."""
        LOGGER.debug("Testing credentials...")
        client = ApiClient(
            username=username,
            password=password,
            session=async_create_clientsession(self.hass),
        )
        await client.async_get_data()
