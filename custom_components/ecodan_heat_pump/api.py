"""Sample API Client."""

from __future__ import annotations
import dataclasses
from enum import Enum
from aiohttp import ClientError, ClientResponseError
from http import HTTPStatus
from dataclasses import dataclass

from .const import LOGGER

import json
import asyncio
import aiohttp
import pymelcloud


class Credentials(Enum):
    """The credentials set identifier"""

    CREDENTIALS_1 = "credentials_1"
    CREDENTIALS_2 = "credentials_2"
    CREDENTIALS_3 = "credentials_3"


class MELCloudApiClientError(Exception):
    """Exception to indicate a general API error."""


class MELCLoudApiClientCommunicationError(MELCloudApiClientError):
    """Exception to indicate a communication error."""


class MELCloudApiClientAuthenticationError(MELCloudApiClientError):
    """Exception to indicate an authentication error."""

    def __init__(self, credentials: Credentials, *args: object) -> None:
        super().__init__(*args)
        self._credentials = credentials

    @property
    def credentials(self) -> Credentials:
        return self._credentials


@dataclass
class HeatPumpState:
    id: str
    has_power: bool
    status: str
    operation_mode: str
    temperature_unit: str
    temperature_increment: str
    wifi_strength: int
    target_flow_temperature: float
    flow_temperature: float
    flow_return_temperature: float
    # forced_hot_water_mode: bool
    # is_offline: bool
    # target_water_tank_temperature: float
    # water_tank_temperature: float
    # outdoor_temperature: float
    # holiday_mode: bool
    # prohibit_heating: bool
    # prohibit_water_heating: bool
    # demand_percentage: float
    # last_cloud_communication: str


class MELCloudApiClient:
    """MELCloud API client"""

    def __init__(
        self,
        credentials: Credentials,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        self._credentials = credentials
        self._session = session
        self._username = username
        self._password = password

    async def async_get_data(self) -> any:
        """Get data from the API."""
        LOGGER.debug(f"Fetching data from MELCloud API using '{self._credentials}'...")
        try:
            # Log in to API
            access_token = await pymelcloud.login(
                self._username, self._password, session=self._session
            )

            # Fetch the first air-to-water device
            devices = await pymelcloud.get_devices(access_token, session=self._session)
            device = devices[pymelcloud.DEVICE_TYPE_ATW][0]

            # Update the device information
            await device.update()

            # Extract the first heating zone
            zones = device.zones
            zone = zones[0]

            # Capture the current state of the heat pump
            heat_pump_state = HeatPumpState(
                id=device.device_id,
                has_power=device.power,
                status=device.status,
                operation_mode=device.operation_mode,
                temperature_unit=device.temp_unit,
                temperature_increment=device.temperature_increment,
                wifi_strength=device.wifi_signal,
                target_flow_temperature=zone.target_flow_temperature,
                flow_temperature=zone.flow_temperature,
                flow_return_temperature=zone.return_temperature,
                # forced_hot_water_mode=[TODO],
                # is_offline=[TODO],
                # target_water_tank_temperature=[TODO],
                # water_tank_temperature=[TODO],
                # outdoor_temperature=[TODO],
                # holiday_mode=[TODO],
                # prohibit_heating=[TODO],
                # prohibit_water_heating=[TODO],
                # demand_percentage=[TODO],
                # last_cloud_communication=[TODO],
            )

            return heat_pump_state
            # return json.dumps(dataclasses.asdict(heat_pump_state))

        except (ClientResponseError, AttributeError) as err:
            if isinstance(err, ClientResponseError) and err.status in (
                HTTPStatus.UNAUTHORIZED,
                HTTPStatus.FORBIDDEN,
            ):
                raise MELCloudApiClientAuthenticationError(
                    self._credentials,
                    "Invalid credentials for MELCloud API!",
                )
            elif isinstance(err, AttributeError) and err.name == "get":
                raise MELCloudApiClientAuthenticationError(
                    self._credentials,
                    "Invalid credentials for MELCloud API!",
                )
            else:
                raise MELCLoudApiClientCommunicationError(
                    self._credentials,
                    "Cannot connect to MELCloud API!",
                )
        except (
            asyncio.TimeoutError,
            ClientError,
        ):
            raise MELCLoudApiClientCommunicationError(
                self._credentials,
                "Cannot connect to MELCloud API!",
            )
