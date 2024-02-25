"""Constants for ecodan_heat_pump."""

from datetime import timedelta
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "Ecodan Heat Pump"
DOMAIN = "ecodan_heat_pump"

MIN_FLOW_TEMP = 25
MAX_FLOW_TEMP = 60

# 5 minute interval per credential = 100s
COORDINATOR_UPDATE_INTERVAL = timedelta(seconds=(5 * 60) / 3)

# A 10s delay before requesting a refresh to allow the heat pump to react
COORDINATOR_REFRESH_DELAY = 5

USERNAME_1 = "username_1"
PASSWORD_1 = "password_1"

USERNAME_2 = "username_2"
PASSWORD_2 = "password_2"

USERNAME_3 = "username_3"
PASSWORD_3 = "password_3"
