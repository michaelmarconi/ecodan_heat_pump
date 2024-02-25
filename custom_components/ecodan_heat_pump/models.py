import datetime  # noqa: D100

from dataclasses import dataclass
from enum import Enum


class CredentialsId(Enum):  # noqa: D101
    CREDENTIALS_1 = "credentials_1"
    CREDENTIALS_2 = "credentials_2"
    CREDENTIALS_3 = "credentials_3"


class HeatingMode(Enum):  # noqa: D101
    FLOW_TEMPERATURE = "heat_flow"
    CURVE_TEMPERATURE = "curve"


class HeatingStatus(Enum):  # noqa: D101
    HEATING = "heating"
    IDLE = "idle"


@dataclass
class Credentials:
    """These are the credentials used to access the MELCloud API."""

    id: CredentialsId
    username: str
    password: str
    access_token: str | None = None


@dataclass
class HeatPumpState:
    """This is the model for the latest state of the heat pump."""

    device_id: str
    wifi_status: str
    wifi_signal_stregth: int
    has_power: bool
    has_error: bool
    is_offline: bool
    is_holiday_mode: bool
    is_defrost_mode: bool
    is_eco_hot_water: bool
    is_heating_prohibited: bool
    is_heating_water_prohibited: bool
    is_forced_to_heat_water: bool
    heating_mode: HeatingMode
    heating_status: HeatingStatus
    target_flow_temperature: float
    flow_temperature: float
    return_temperature: float
    target_water_tank_temperature: float
    water_tank_temperature: float
    outdoor_temperature: float
    last_communication: datetime
    rate_of_current_energy_consumption: float
    rate_of_current_energy_production: float
    current_coefficient_of_performance: float
    daily_energy_report_date: datetime
    daily_heating_energy_consumed: float
    daily_heating_energy_produced: float
    daily_hot_water_energy_consumed: float
    daily_hot_water_energy_produced: float
    daily_total_energy_consumed: float
    daily_total_energy_produced: float
    daily_coefficient_of_performance: float
