"""Sample API Client."""

from __future__ import annotations
from dateutil import parser

import asyncio
import socket
import json
import aiohttp
import async_timeout

from custom_components.ecodan_heat_pump.errors import (
    ApiClientAuthenticationException,
    ApiClientCommunicationException,
    ApiClientException,
)
from custom_components.ecodan_heat_pump.models import (
    Credentials,
    CredentialsId,
    HeatPumpState,
    HeatingMode,
    HeatingStatus,
)
from custom_components.ecodan_heat_pump.const import LOGGER

BASE_URL = "https://app.melcloud.com/Mitsubishi.Wifi.Client"
LOGIN_URL = f"{BASE_URL}/Login/ClientLogin"
LIST_DEVICES_URL = f"{BASE_URL}/User/ListDevices"
SETTINGS_URL = f"{BASE_URL}/Device/SetAtw"


class ApiClient:
    """This is the MELCLoud API client."""

    def __init__(  # noqa: D107
        self,
        credentials: list[Credentials],
        session: aiohttp.ClientSession,
    ) -> None:
        self._session = session
        self._credentials = credentials
        self._credentials_last_used: Credentials = None

    async def async_get_data(self) -> HeatPumpState:
        """Update the heat pump state model."""

        # Get the next set of credentials to use
        credentials = await self._async_get_next_credentials()

        # List data about all devices
        response = await self._async_api_get(LIST_DEVICES_URL, credentials)

        # Update the stored heat pump state from the API request
        heat_pump_state = self._map_response_to_heat_pump_state(response)

        return heat_pump_state

    async def async_toggle_heat_pump_power(self, deviceId: str, power: bool) -> bool:
        """Toggle the heat pump power on or off."""

        # Get the next set of credentials to use
        credentials = await self._async_get_next_credentials()

        # Set state using the API
        response = await self._async_api_post(
            SETTINGS_URL,
            credentials,
            {"EffectiveFlags": 1, "DeviceID": deviceId, "Power": power},
        )

        # Extract the updated power attribute from the response
        has_power: bool = response["Power"]

        return has_power

    async def async_toggle_water_heating(self, deviceId: str, heat_water: bool) -> bool:
        """Toggle hot water heating on/off."""

        LOGGER.debug(f"Toggling water heating to '{heat_water}'...")

        # Get the next set of credentials to use
        credentials = await self._async_get_next_credentials()

        # Configure the request data
        data = {
            "EffectiveFlags": 0x10000,
            "ForcedHotWaterMode": heat_water,
            "DeviceID": deviceId,
        }

        # Set state using the API
        response = await self._async_api_post(SETTINGS_URL, credentials, data)

        # Extract the updated power attribute from the response
        forced_hot_water_mode: bool = response["ForcedHotWaterMode"]

        return forced_hot_water_mode

    async def async_set_heating_mode(
        self, deviceId: str, heating_mode: HeatingMode | None
    ) -> HeatingMode:
        """Set the heating mode (flow/curve)."""

        LOGGER.debug(f"Setting heating mode to'{heating_mode}'...")

        OPERATION_MODE_FLOW = 1
        OPERATION_MODE_CURVE = 2

        # Get the next set of credentials to use
        credentials = await self._async_get_next_credentials()

        # Configure the request data
        data = {
            "EffectiveFlags": None,
            "OperationModeZone1": None,
            "DeviceID": deviceId,
        }
        if heating_mode == HeatingMode.FLOW_TEMPERATURE:
            data["EffectiveFlags"] = 67108872
            data["OperationModeZone1"] = OPERATION_MODE_FLOW
        elif heating_mode == HeatingMode.CURVE_TEMPERATURE:
            data["EffectiveFlags"] = 281475043819560
            data["OperationModeZone1"] = OPERATION_MODE_CURVE

        # Set state using the API
        response = await self._async_api_post(SETTINGS_URL, credentials, data)

        # Extract the updated power attribute from the response
        operation_mode: int = response["OperationModeZone1"]

        if operation_mode == OPERATION_MODE_CURVE:
            return HeatingMode.CURVE_TEMPERATURE
        elif operation_mode == OPERATION_MODE_FLOW:
            return HeatingMode.FLOW_TEMPERATURE
        else:
            return None

    async def async_set_flow_temperature(
        self, deviceId: str, flow_temperature: float, hot_water_temperature: float
    ) -> float:
        """Set the flow temperature for heating. If you don't also set the hot water temperature, it lowers it to the minimum!."""

        LOGGER.debug(f"Setting flow temperature to '{flow_temperature}'...")

        # Get the next set of credentials to use
        credentials = await self._async_get_next_credentials()

        # Configure the request data
        data = {
            "EffectiveFlags": 281475043819552,
            "SetHeatFlowTemperatureZone1": flow_temperature,
            "SetTankWaterTemperature": hot_water_temperature,
            "DeviceID": deviceId,
        }

        # Set state using the API
        response = await self._async_api_post(SETTINGS_URL, credentials, data)

        # Extract the updated power attribute from the response
        flow_temperature: float = response["SetHeatFlowTemperatureZone1"]

        return flow_temperature

    async def _async_get_next_credentials(self) -> Credentials:
        """Get the next set of credentials to use in the series."""
        next_credentials: Credentials
        if self._credentials_last_used is None:
            next_credentials = self._credentials[0]
            self._credentials_last_used = next_credentials
        else:
            match self._credentials_last_used.id:
                case CredentialsId.CREDENTIALS_1:
                    next_credentials = self._credentials[1]
                case CredentialsId.CREDENTIALS_2:
                    next_credentials = self._credentials[2]
                case CredentialsId.CREDENTIALS_3:
                    next_credentials = self._credentials[0]
            self._credentials_last_used = next_credentials

        # Log in and get an access token if necessary
        if next_credentials.access_token is None:
            await self._async_login(next_credentials)

        LOGGER.debug(f"Using credentials '{next_credentials.id}'...")
        return next_credentials

    async def _async_login(self, credentials: Credentials):
        """Log in and get an access token, which is stored in the credentials."""
        if credentials.access_token is not None:
            raise ApiClientException(
                f"Credentials '{credentials.id}' already has an access token!"
            )
        response = await self._async_api_post(
            url=LOGIN_URL,
            credentials=None,
            data={
                "Email": credentials.username,
                "Password": credentials.password,
                "AppVersion": "1.19.1.1",
                "Persist": "true",
            },
        )
        errorId = response["ErrorId"]
        if errorId is not None:
            raise ApiClientAuthenticationException(
                f"Log in failed with credentials '{credentials.id}' ({credentials.username})!"
            )

        try:
            contextKey = response["LoginData"]["ContextKey"]
            credentials.access_token = contextKey
            LOGGER.debug(
                f"Successfully requested access token for credentials '{credentials.id}'."
            )
        except Exception as exception:
            raise ApiClientException(
                "Failed to extract API token from log in request!"
            ) from exception
        return

    def _map_response_to_heat_pump_state(self, response: json) -> HeatPumpState:
        """Map the response from the API to the heat pump state model."""

        try:
            heat_pump_data = response[0]
            device = heat_pump_data["Structure"]["Devices"][0]["Device"]
            heat_pump_state = HeatPumpState(
                device_id=device["DeviceID"],
                wifi_status=device["WifiAdapterStatus"],
                wifi_signal_stregth=device["WifiSignalStrength"],
                has_power=device["Power"],
                has_error=device["HasError"],
                is_offline=device["Offline"],
                is_holiday_mode=device["HolidayMode"],
                is_defrost_mode=device["DefrostMode"] == 1,
                is_eco_hot_water=device["EcoHotWater"],
                is_heating_prohibited=device["ProhibitHeatingZone1"],
                is_heating_water_prohibited=device["ProhibitHotWater"],
                is_forced_to_heat_water=device["ForcedHotWaterMode"],
                heating_mode=self._determine_heating_mode(device),
                heating_status=self._determine_heating_status(device),
                target_flow_temperature=device["SetHeatFlowTemperatureZone1"],
                flow_temperature=device["FlowTemperature"],
                return_temperature=device["ReturnTemperature"],
                target_water_tank_temperature=device["SetTankWaterTemperature"],
                water_tank_temperature=device["TankWaterTemperature"],
                outdoor_temperature=device["OutdoorTemperature"],
                last_communication=parser.parse(device["LastTimeStamp"]),
                rate_of_current_energy_consumption=device["CurrentEnergyConsumed"],
                rate_of_current_energy_production=device["CurrentEnergyProduced"],
                current_coefficient_of_performance=self._determine_current_coefficient_of_performance(
                    device
                ),
                daily_energy_report_date=parser.parse(
                    device["DailyEnergyConsumedDate"]
                ).date(),
                daily_heating_energy_consumed=device["DailyHeatingEnergyConsumed"],
                daily_heating_energy_produced=device["DailyHeatingEnergyProduced"],
                daily_hot_water_energy_consumed=device["DailyHotWaterEnergyConsumed"],
                daily_hot_water_energy_produced=device["DailyHotWaterEnergyProduced"],
                daily_total_energy_consumed=self._determine_daily_total_energy_consumed(
                    device
                ),
                daily_total_energy_produced=self._determine_daily_total_energy_produced(
                    device
                ),
                daily_coefficient_of_performance=self._determine_daily_coefficient_of_performance(
                    device
                ),
            )
            return heat_pump_state
        except Exception as exception:
            LOGGER.exception(exception)
            raise ApiClientException(
                "Failed to map API data to heat pump state!"
            ) from exception

    def _determine_daily_coefficient_of_performance(self, device):
        daily_total_energy_consumed = self._determine_daily_total_energy_consumed(
            device
        )
        daily_total_energy_produced = self._determine_daily_total_energy_produced(
            device
        )
        return (
            round(daily_total_energy_produced / daily_total_energy_consumed, 2)
            if daily_total_energy_consumed > 0
            else 0
        )

    def _determine_daily_total_energy_produced(self, device):
        return round(
            device["DailyHeatingEnergyProduced"]
            + device["DailyHotWaterEnergyProduced"],
            2,
        )

    def _determine_daily_total_energy_consumed(self, device):
        return round(
            device["DailyHeatingEnergyConsumed"]
            + device["DailyHotWaterEnergyConsumed"],
            2,
        )

    def _determine_heating_status(self, device) -> HeatingStatus:
        return (
            HeatingStatus.IDLE if device["IdleZone1"] is True else HeatingStatus.HEATING
        )

    def _determine_heating_mode(self, device) -> HeatingMode | None:
        operation_mode = device["OperationModeZone1"]
        if operation_mode == 1:
            return HeatingMode.FLOW_TEMPERATURE
        elif operation_mode == 2:
            return HeatingMode.CURVE_TEMPERATURE
        else:
            return None

    def _determine_current_coefficient_of_performance(self, device) -> float:
        return (
            round(device["CurrentEnergyProduced"] / device["CurrentEnergyConsumed"], 2)
            if device["CurrentEnergyConsumed"] > 0
            else 0
        )

    async def _async_api_post(
        self,
        url,
        credentials: Credentials | None,
        data: dict,
    ) -> any:
        """Post data to the MELCloud API."""
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Host": "app.melcloud.com",
            "Pragma": "no-cache",
            "Referer": "https://app.melcloud.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Safari/605.1.15",
            "X-Requested-With": "XMLHttpRequest",
        }
        if credentials is not None:
            headers["X-MitsContextKey"] = credentials.access_token

        try:
            async with async_timeout.timeout(10):
                response = await self._session.post(
                    url=url,
                    headers=headers,
                    json=data,
                )
                if response.status in (401, 403):
                    raise ApiClientAuthenticationException(
                        "Invalid credentials",
                    )
                response.raise_for_status()
                return await response.json()

        except asyncio.TimeoutError as exception:
            raise ApiClientCommunicationException(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise ApiClientCommunicationException(
                "Error fetching information",
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise ApiClientException("Something really wrong happened!") from exception

    async def _async_api_get(
        self,
        url,
        credentials: Credentials,
    ) -> any:
        """Get data from the MELCloud API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.get(
                    url=url,
                    headers={
                        "Accept": "application/json, text/javascript, */*; q=0.01",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Accept-Language": "en-GB,en;q=0.9",
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "Host": "app.melcloud.com",
                        "Pragma": "no-cache",
                        "Referer": "https://app.melcloud.com/",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-origin",
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Safari/605.1.15",
                        "X-MitsContextKey": credentials.access_token,
                        "X-Requested-With": "XMLHttpRequest",
                    },
                )
                if response.status in (401, 403):
                    raise ApiClientAuthenticationException(
                        "Invalid credentials",
                    )
                response.raise_for_status()
                return await response.json()

        except asyncio.TimeoutError as exception:
            raise ApiClientCommunicationException(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise ApiClientCommunicationException(
                "Error fetching information",
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise ApiClientException("Something really wrong happened!") from exception
