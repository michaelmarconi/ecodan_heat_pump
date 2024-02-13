from dataclasses import dataclass
from enum import Enum


class CredentialsId(Enum):
    """The credentials set identifier"""

    CREDENTIALS_1 = "credentials_1"
    CREDENTIALS_2 = "credentials_2"
    CREDENTIALS_3 = "credentials_3"


@dataclass
class Credentials:
    id: CredentialsId
    username: str
    password: str


@dataclass
class HeatPumpState:
    id: str
    has_power: bool
    status: str
    device_operation_mode: str
    zone_operation_mode: str
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
