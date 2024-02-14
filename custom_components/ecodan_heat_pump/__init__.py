"""Custom integration to integrate ecodan_heat_pump with Home Assistant.

For more details about this integration, please refer to
https://github.com/michaelmarconi/ecodan_heat_pump
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.ecodan_heat_pump.models import Credentials

from .api import CredentialsId, ApiClient
from .const import DOMAIN, PASSWORD_1, PASSWORD_2, USERNAME_1, USERNAME_2, USERNAME_3
from .coordinator import EcodanHeatPumpDataUpdateCoordinator
from .const import (
    PASSWORD_3,
)

PLATFORMS: list[Platform] = [
    # Platform.SENSOR,
    # Platform.BINARY_SENSOR,
    # Platform.SWITCH,
    Platform.CLIMATE,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})

    # Assemble credentials from pre-existing config
    credentials_1 = Credentials(
        CredentialsId.CREDENTIALS_1, entry.data[USERNAME_1], entry.data[PASSWORD_1]
    )
    credentials_2 = Credentials(
        CredentialsId.CREDENTIALS_2, entry.data[USERNAME_2], entry.data[PASSWORD_2]
    )
    credentials_3 = Credentials(
        CredentialsId.CREDENTIALS_3, entry.data[USERNAME_3], entry.data[PASSWORD_3]
    )

    # Set up data coordinator
    hass.data[DOMAIN][entry.entry_id] = coordinator = (
        EcodanHeatPumpDataUpdateCoordinator(
            hass=hass,
            client=ApiClient(
                credentials=[credentials_1, credentials_2, credentials_3],
                session=async_get_clientsession(hass),
            ),
        )
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
