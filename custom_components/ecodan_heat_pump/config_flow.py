"""Adds config flow for Blueprint."""

from __future__ import annotations
from typing import Any, Mapping

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, FlowResult
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import (
    DOMAIN,
    LOGGER,
    PASSWORD_1,
    PASSWORD_2,
    PASSWORD_3,
    USERNAME_1,
    USERNAME_2,
    USERNAME_3,
)


class ConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        LOGGER.debug("Setting up API credentials...")
        _errors = {}
        self._entry_data = user_input if user_input != None else {}
        # TODO: fixme!
        # if user_input is not None:
        #     try:
        #         await self._test_credentials(user_input)
        #     except MELCloudApiClientAuthenticationError as exception:
        #         _errors["base"] = exception.credentials
        #     except MELCLoudApiClientCommunicationError as exception:
        #         LOGGER.error(exception)
        #         _errors["base"] = "connection"
        #     except MELCloudApiClientError as exception:
        #         _errors["base"] = "unknown"
        #     else:
        #         return self.async_create_entry(
        #             title="Ecodan Heat Pump",
        #             data=user_input,
        #         )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        USERNAME_1, default=(self._entry_data or {}).get(USERNAME_1)
                    ): TextSelector(
                        TextSelectorConfig(
                            type=TextSelectorType.TEXT, autocomplete="username"
                        )
                    ),
                    vol.Required(
                        PASSWORD_1, default=(self._entry_data or {}).get(PASSWORD_1)
                    ): TextSelector(
                        TextSelectorConfig(
                            type=TextSelectorType.PASSWORD, autocomplete="password"
                        )
                    ),
                    vol.Required(
                        USERNAME_2, default=(user_input or {}).get(USERNAME_2)
                    ): TextSelector(
                        TextSelectorConfig(
                            type=TextSelectorType.TEXT, autocomplete="username"
                        )
                    ),
                    vol.Required(
                        PASSWORD_2, default=(user_input or {}).get(PASSWORD_2)
                    ): TextSelector(
                        TextSelectorConfig(
                            type=TextSelectorType.PASSWORD, autocomplete="password"
                        )
                    ),
                    vol.Required(
                        USERNAME_3, default=(user_input or {}).get(USERNAME_3)
                    ): TextSelector(
                        TextSelectorConfig(
                            type=TextSelectorType.TEXT, autocomplete="username"
                        )
                    ),
                    vol.Required(
                        PASSWORD_3, default=(user_input or {}).get(PASSWORD_3)
                    ): TextSelector(
                        TextSelectorConfig(
                            type=TextSelectorType.PASSWORD, autocomplete="password"
                        )
                    ),
                }
            ),
            errors=_errors,
        )

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> FlowResult:
        LOGGER.debug("Starting re-auth flow...")
        return await self.async_step_user(entry_data)

    async def _test_credentials(
        self,
        user_input: dict,
    ) -> None:
        """Validate credentials."""
        LOGGER.debug("Validating API credentials...")
        # TODO: fixme
        # client_1 = MELCloudApiClient(
        #     credentials=CredentialsId.CREDENTIALS_1,
        #     username_1=user_input[USERNAME_1],
        #     password_1=user_input[PASSWORD_1],
        #     session=async_create_clientsession(self.hass),
        # )
        # await client_1.async_get_data()
        # client_2 = MELCloudApiClient(
        #     credentials=CredentialsId.CREDENTIALS_2,
        #     username_1=user_input[USERNAME_2],
        #     password_1=user_input[PASSWORD_2],
        #     session=async_create_clientsession(self.hass),
        # )
        # await client_2.async_get_data()
        # client_3 = MELCloudApiClient(
        #     credentials=CredentialsId.CREDENTIALS_3,
        #     username_1=user_input[USERNAME_3],
        #     password_1=user_input[PASSWORD_3],
        #     session=async_create_clientsession(self.hass),
        # )
        # await client_3.async_get_data()
