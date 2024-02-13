"""Sample API Client."""

from __future__ import annotations
from aiohttp import ClientError, ClientResponseError
from http import HTTPStatus

from .models import Credentials, CredentialsId, HeatPumpState
from .const import LOGGER

import asyncio
import aiohttp
import pymelcloud

from pymelcloud.atw_device import (
    Device,
    OPERATION_MODE_AUTO,
    OPERATION_MODE_FORCE_HOT_WATER,
    STATUS_HEAT_WATER,
    STATUS_HEAT_ZONES,
    STATUS_STANDBY,
    STATUS_UNKNOWN,
    ZONE_OPERATION_MODE_CURVE,
    ZONE_OPERATION_MODE_HEAT_FLOW,
    ZONE_OPERATION_MODE_HEAT_THERMOSTAT,
    ZONE_STATUS_HEAT,
    ZONE_STATUS_IDLE,
    ZONE_STATUS_UNKNOWN,
)


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
        self._devices: list[Device] = []
        self._last_used_device: int = None

    async def async_get_next_device(self) -> Device:
        """Get the next device in the rotation, creating it if necessary"""
        if self._last_used_device == None:
            device = await self.async_login_and_get_device(self._credentials[0])
            self._devices.append(device)
            self._last_used_device = 0
            return device
        else:
            next_device_index = self._last_used_device + 1
            if next_device_index == 3:
                next_device_index = 0  # Wrap around to the first device
            LOGGER.debug(f"Next device index: {next_device_index}")

            try:
                next_device = self._devices[next_device_index]
                LOGGER.debug(f"Reusing existing device {next_device_index}...")
                self._last_used_device = next_device_index
                return next_device
            except IndexError:
                LOGGER.debug("There was no next device")
                device = await self.async_login_and_get_device(
                    self._credentials[next_device_index]
                )
                self._devices.append(device)
                self._last_used_device = next_device_index
                return device

    async def async_login_and_get_device(self, credentials: Credentials) -> Device:
        """Log in and get a device using the supplied credentials"""
        try:
            LOGGER.debug(f"Creating a device for {credentials.id}...")
            # Get an access token for the API
            access_token = await pymelcloud.login(
                credentials.username,
                credentials.password,
                session=self._session,
            )
            # Return the first air-to-water device
            devices = await pymelcloud.get_devices(access_token, session=self._session)
            return devices[pymelcloud.DEVICE_TYPE_ATW][0]
        except (ClientResponseError, AttributeError) as err:
            if isinstance(err, ClientResponseError) and err.status in (
                HTTPStatus.UNAUTHORIZED,
                HTTPStatus.FORBIDDEN,
            ):
                raise MELCloudApiClientAuthenticationError(
                    credentials,
                    "Invalid credentials for MELCloud API!",
                )
            elif isinstance(err, AttributeError) and err.name == "get":
                raise MELCloudApiClientAuthenticationError(
                    credentials,
                    "Invalid credentials for MELCloud API!",
                )
            else:
                raise MELCLoudApiClientCommunicationError(
                    credentials,
                    "Cannot connect to MELCloud API!",
                )
        except (
            asyncio.TimeoutError,
            ClientError,
        ):
            raise MELCLoudApiClientCommunicationError(
                credentials,
                "Cannot connect to MELCloud API!",
            )

    async def async_get_data(self) -> HeatPumpState:
        """Get data from the API."""

        # Get the next device in the series
        device = await self.async_get_next_device()

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

    async def async_switch_off_heat_pump(self):
        """Switch off the heat pump"""

        # Get the next device in the series
        device = await self.async_get_next_device()

        # Switch off the heat pump
        await device.set({"power": False})

        return
