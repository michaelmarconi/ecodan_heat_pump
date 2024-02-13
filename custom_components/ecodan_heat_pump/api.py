"""Sample API Client."""

from __future__ import annotations
from aiohttp import ClientError, ClientResponseError
from http import HTTPStatus

from .models import Credentials, CredentialsId, HeatPumpState
from .const import LOGGER

import asyncio
import aiohttp
import pymelcloud


class MELCloudApiClientError(Exception):
    """Exception to indicate a general API error."""


class MELCLoudApiClientCommunicationError(MELCloudApiClientError):
    """Exception to indicate a communication error."""


class MELCloudApiClientAuthenticationError(MELCloudApiClientError):
    """Exception to indicate an authentication error."""

    def __init__(self, credentials: CredentialsId, *args: object) -> None:
        super().__init__(*args)
        self._credentials = credentials

    @property
    def credentials(self) -> CredentialsId:
        return self._credentials


class MELCloudApiClient:
    """MELCloud API client"""

    def __init__(
        self,
        credentials: list[Credentials],
        session: aiohttp.ClientSession,
    ) -> None:
        self._session = session
        self._credentials = credentials
        self._last_used_credentials: Credentials = None

    async def async_get_data(self) -> any:
        """Get data from the API."""

        # Rotate the credentials to use for the API calls
        credentials_to_use: Credentials
        if self._last_used_credentials == None:
            credentials_to_use = self._credentials[0]
            self._last_used_credentials = self._credentials[0]
        elif self._last_used_credentials == self._credentials[0]:
            credentials_to_use = self._credentials[1]
            self._last_used_credentials = self._credentials[1]
        elif self._last_used_credentials == self._credentials[1]:
            credentials_to_use = self._credentials[2]
            self._last_used_credentials = self._credentials[2]
        elif self._last_used_credentials == self._credentials[2]:
            credentials_to_use = self._credentials[0]
            self._last_used_credentials = self._credentials[0]
        LOGGER.debug(
            f"Fetching data from MELCloud API using '{credentials_to_use.id}'..."
        )

        try:
            # Get an access token for the API
            access_token = await pymelcloud.login(
                credentials_to_use.username,
                credentials_to_use.password,
                session=self._session,
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
                device_operation_mode=device.operation_mode,
                zone_operation_mode=zone.operation_mode,
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
