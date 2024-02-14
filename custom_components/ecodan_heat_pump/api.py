"""Sample API Client."""

from __future__ import annotations
from dateutil import parser

import asyncio
import socket
import json
import aiohttp
import async_timeout

from .models import (
    Credentials,
    CredentialsId,
    HeatPumpState,
    HeatingMode,
    HeatingStatus,
    TargetTemperatureType,
)
from .const import LOGGER

BASE_URL = "https://app.melcloud.com/Mitsubishi.Wifi.Client"
LOGIN_URL = f"{BASE_URL}/Login/ClientLogin"
LIST_DEVICES_URL = f"{BASE_URL}/User/ListDevices"


class ApiClientError(Exception):
    """Exception to indicate a general API error."""


class ApiClientCommunicationError(ApiClientError):
    """Exception to indicate a communication error."""


class ApiClientAuthenticationError(ApiClientError):
    """Exception to indicate an authentication error."""


class ApiClient:
    """This is the MELCLoud API client"""

    def __init__(
        self,
        credentials: list[Credentials],
        session: aiohttp.ClientSession,
    ) -> None:
        self._credentials = credentials
        self._credentials_last_used: Credentials = None
        self._session = session

    def get_next_credentials(self) -> Credentials:
        """Get the next set of credentials to use in the series"""
        if self._credentials_last_used == None:
            next_credentials = self._credentials[0]
            self._credentials_last_used = next_credentials
            return next_credentials
        else:
            next_credentials: Credentials
            match self._credentials_last_used.id:
                case CredentialsId.CREDENTIALS_1:
                    next_credentials = self._credentials[1]
                case CredentialsId.CREDENTIALS_2:
                    next_credentials = self._credentials[2]
                case CredentialsId.CREDENTIALS_3:
                    next_credentials = self._credentials[0]
            self._credentials_last_used = next_credentials
            LOGGER.debug(f"Using credentials '{next_credentials.id}'...")
            return next_credentials

    async def async_login(self, credentials: Credentials):
        """Log in and get an access token, which is stored in the credentials"""
        if credentials.access_token != None:
            raise ApiClientError(
                f"Credentials '{credentials.id}' already has an access token!"
            )
        response = await self.async_api_post(
            LOGIN_URL,
            {
                "Email": credentials.username,
                "Password": credentials.password,
                "AppVersion": "1.19.1.1",
                "Persist": "true",
            },
        )
        errorId = response["ErrorId"]
        if errorId != None:
            raise ApiClientAuthenticationError(
                f"Log in failed with credentials '{credentials.id}'!"
            )

        try:
            contextKey = response["LoginData"]["ContextKey"]
            credentials.access_token = contextKey
            LOGGER.debug(
                f"Successfully requested access token for credentials '{credentials.id}'."
            )
        except Exception as exception:
            raise ApiClientError(
                "Failed to extract API token from log in request!"
            ) from exception
        return

    async def async_get_data(self) -> HeatPumpState:
        """Update the heat pump state model"""

        # Get the next set of credentials to use
        credentials = self.get_next_credentials()

        # Log in and get an access token if necessary
        if credentials.access_token == None:
            await self.async_login(credentials)

        # List data about all devices
        data = await self.async_api_get(LIST_DEVICES_URL, credentials)

        heat_pump_state = self.map_api_data(data)

        LOGGER.debug(heat_pump_state)
        return heat_pump_state

    def map_api_data(self, data: json) -> HeatPumpState:
        """Map the response from the API to the heat pump state model"""
        try:
            heat_pump_data = data[0]
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
                heating_mode=(
                    HeatingMode.AUTO
                    if device["OperationMode"] == 1
                    else (
                        HeatingMode.HEAT_WATER if device["OperationMode"] == 2 else None
                    )
                ),
                heating_status=(
                    HeatingStatus.IDLE
                    if device["IdleZone1"] == True
                    else HeatingStatus.HEATING
                ),
                target_temperature_type=(
                    TargetTemperatureType.ROOM_TEMPERATURE
                    if device["OperationModeZone1"] == 0
                    else (
                        TargetTemperatureType.FLOW_TEMPERATURE
                        if device["OperationModeZone1"] == 1
                        else (
                            TargetTemperatureType.CURVE_TEMPERATURE
                            if device["OperationModeZone1"] == 2
                            else None
                        )
                    )
                ),
                target_flow_temperature=device["SetHeatFlowTemperatureZone1"],
                flow_temperature=device["FlowTemperature"],
                return_temperature=device["ReturnTemperature"],
                target_water_tank_temperature=device["SetTankWaterTemperature"],
                water_tank_temperature=device["TankWaterTemperature"],
                outdoor_temperature=device["OutdoorTemperature"],
                demand_percentage=device["DemandPercentage"],
                last_communication=parser.parse(device["LastTimeStamp"]),
                rate_of_current_energy_consumption=device["CurrentEnergyConsumed"],
                rate_of_current_energy_production=device["CurrentEnergyProduced"],
                current_coefficient_of_performance=(
                    device["CurrentEnergyConsumed"] / device["CurrentEnergyProduced"]
                    if device["CurrentEnergyProduced"] > 0
                    else 0
                ),
                daily_energy_report_date=parser.parse(
                    device["DailyEnergyConsumedDate"]
                ),
                daily_heating_energy_consumed=device["DailyHeatingEnergyConsumed"],
                daily_heating_energy_produced=device["DailyHeatingEnergyProduced"],
                daily_hot_water_energy_consumed=device["DailyHotWaterEnergyConsumed"],
                daily_hot_water_energy_produced=device["DailyHotWaterEnergyProduced"],
                daily_total_energy_consumed=(
                    device["DailyHeatingEnergyConsumed"]
                    + device["DailyHotWaterEnergyConsumed"]
                ),
                daily_total_energy_produced=(
                    device["DailyHeatingEnergyProduced"]
                    + device["DailyHotWaterEnergyProduced"]
                ),
                daily_coefficient_of_performance=(
                    (
                        device["DailyHeatingEnergyConsumed"]
                        + device["DailyHotWaterEnergyConsumed"]
                    )
                    / (
                        device["DailyHeatingEnergyProduced"]
                        + device["DailyHotWaterEnergyProduced"]
                    )
                    if (
                        device["DailyHeatingEnergyProduced"]
                        + device["DailyHotWaterEnergyProduced"]
                    )
                    > 0
                    else 0
                ),
            )
            return heat_pump_state
        except Exception as exception:
            LOGGER.exception(exception)
            raise ApiClientError(
                "Failed to map API data to heat pump state!"
            ) from exception

    async def async_api_post(
        self,
        url,
        data: dict,
    ) -> any:
        """Post data to the MELCloud API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.post(url=url, headers={}, data=data)
                if response.status in (401, 403):
                    raise ApiClientAuthenticationError(
                        "Invalid credentials",
                    )
                response.raise_for_status()
                return await response.json()

        except asyncio.TimeoutError as exception:
            raise ApiClientCommunicationError(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise ApiClientCommunicationError(
                "Error fetching information",
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise ApiClientError("Something really wrong happened!") from exception

    async def async_api_get(
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
                    raise ApiClientAuthenticationError(
                        "Invalid credentials",
                    )
                response.raise_for_status()
                return await response.json()

        except asyncio.TimeoutError as exception:
            raise ApiClientCommunicationError(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise ApiClientCommunicationError(
                "Error fetching information",
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise ApiClientError("Something really wrong happened!") from exception

    # async def _api_wrapper(
    #     self,
    #     method: str,
    #     url: str,
    #     data: dict | None = None,
    #     headers: dict | None = None,
    # ) -> any:
    #     """Get information from the API."""
    #     try:
    #         async with async_timeout.timeout(10):
    #             response = await self._session.request(
    #                 method=method,
    #                 url=url,
    #                 headers=headers,
    #                 json=data,
    #             )
    #             if response.status in (401, 403):
    #                 raise ApiClientAuthenticationError(
    #                     "Invalid credentials",
    #                 )
    #             response.raise_for_status()
    #             return await response.json()

    #     except asyncio.TimeoutError as exception:
    #         raise ApiClientCommunicationError(
    #             "Timeout error fetching information",
    #         ) from exception
    #     except (aiohttp.ClientError, socket.gaierror) as exception:
    #         raise ApiClientCommunicationError(
    #             "Error fetching information",
    #         ) from exception
    #     except Exception as exception:  # pylint: disable=broad-except
    #         raise ApiClientError("Something really wrong happened!") from exception
