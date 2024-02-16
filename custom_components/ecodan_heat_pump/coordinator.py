"""DataUpdateCoordinator for ecodan_heat_pump."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from custom_components.ecodan_heat_pump.api import ApiClient
from custom_components.ecodan_heat_pump.errors import (
    ApiClientAuthenticationException,
    ApiClientException,
)
from custom_components.ecodan_heat_pump.const import DOMAIN, LOGGER
from custom_components.ecodan_heat_pump.models import HeatPumpState


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class Coordinator(DataUpdateCoordinator):
    """Data coordinator using a data store to limit impact on API"""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: ApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=(5 * 60) / 3
            ),  # 5 minute interval per credential = 100s
        )

    async def _async_update_data(self):
        """Refresh the data in the coordinator using the underlying API client"""
        try:
            return await self.client.async_get_data()
        except ApiClientAuthenticationException as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except ApiClientException as exception:
            raise UpdateFailed(exception) from exception

    async def async_toggle_heat_pump_power(self, power: bool):
        """Toggle the heat pump power on or off"""

        # Get the heat pump state from the coordinator
        heat_pump_state: HeatPumpState = self.data

        # Toggle the heat pump power using the API
        has_power = await self.client.async_toggle_heat_pump_power(
            deviceId=heat_pump_state.device_id,
            power=power,
        )

        # Update the coordinator data
        heat_pump_state.has_power = has_power
        self.async_set_updated_data(heat_pump_state)
