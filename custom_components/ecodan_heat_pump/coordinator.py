"""DataUpdateCoordinator for ecodan_heat_pump."""

from __future__ import annotations

import asyncio

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
from custom_components.ecodan_heat_pump.const import (
    COORDINATOR_REFRESH_DELAY,
    COORDINATOR_UPDATE_INTERVAL,
    DOMAIN,
    LOGGER,
)
from custom_components.ecodan_heat_pump.models import HeatPumpState, HeatingMode


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class Coordinator(DataUpdateCoordinator):
    """Data coordinator using a data store to limit impact on API."""

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
            update_interval=COORDINATOR_UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        """Refresh the data in the coordinator using the underlying API client."""
        try:
            return await self.client.async_get_data()
        except ApiClientAuthenticationException as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except ApiClientException as exception:
            raise UpdateFailed(exception) from exception

    async def async_toggle_heat_pump_power(self, power: bool):
        """Toggle the heat pump power on or off."""

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

        # Request a state update
        await asyncio.sleep(COORDINATOR_REFRESH_DELAY)
        await self.async_request_refresh()

        return

    async def async_toggle_water_heating(self, heat_water: bool):
        """Toggle hot water heating on/off."""

        # Get the heat pump state from the coordinator
        heat_pump_state: HeatPumpState = self.data

        # Toggle the heat pump power using the API
        is_forced_to_heat_water = await self.client.async_toggle_water_heating(
            deviceId=heat_pump_state.device_id,
            heat_water=heat_water,
        )

        # Update the coordinator data
        heat_pump_state.is_forced_to_heat_water = is_forced_to_heat_water
        self.async_set_updated_data(heat_pump_state)

        # Request a state update
        await asyncio.sleep(COORDINATOR_REFRESH_DELAY)
        await self.async_request_refresh()

        return

    async def async_set_heating_mode(self, heating_mode: HeatingMode):
        """Set the heating mode (flow/curve)."""

        # Get the heat pump state from the coordinator
        heat_pump_state: HeatPumpState = self.data

        # Set the heat pump operation mode using the API
        heating_mode = await self.client.async_set_heating_mode(
            deviceId=heat_pump_state.device_id,
            heating_mode=heating_mode,
        )

        # Update the coordinator data
        heat_pump_state.heating_mode = heating_mode
        self.async_set_updated_data(heat_pump_state)

        # Request a state update
        await asyncio.sleep(COORDINATOR_REFRESH_DELAY)
        await self.async_request_refresh()

        return

    async def async_set_flow_temperature(self, temperature: float):
        """Set the flow temperature for heating."""

        # Get the heat pump state from the coordinator
        heat_pump_state: HeatPumpState = self.data

        # Set the heat pump operation mode using the API
        target_flow_temperature = await self.client.async_set_flow_temperature(
            deviceId=heat_pump_state.device_id,
            flow_temperature=temperature,
            hot_water_temperature=heat_pump_state.target_water_tank_temperature,
        )

        # Update the coordinator data
        heat_pump_state.target_flow_temperature = target_flow_temperature
        self.async_set_updated_data(heat_pump_state)

        # Request a state update
        await asyncio.sleep(COORDINATOR_REFRESH_DELAY)
        await self.async_request_refresh()

        return
