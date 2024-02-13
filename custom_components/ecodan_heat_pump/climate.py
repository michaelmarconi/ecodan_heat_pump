"""Switch platform for ecodan_heat_pump."""

from __future__ import annotations

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
)
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT,
    HVAC_MODE_AUTO,
    HVAC_MODE_OFF,
    HVACAction,
    PRESET_NONE,
    PRESET_BOOST,
)
from homeassistant.const import TEMP_CELSIUS

from pymelcloud.atw_device import (
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

from custom_components.ecodan_heat_pump.api import HeatPumpState

from .const import DOMAIN, LOGGER
from .coordinator import EcodanHeatPumpDataUpdateCoordinator
from .entity import EcodanHeatPumpEntity

ENTITY_DESCRIPTIONS = (
    ClimateEntityDescription(
        key=DOMAIN,
        name="Ecodan Heat Pump Thermostat",
        icon="mdi:heat-pump-outline",
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the climate platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        EcodanHeatPumpThermostatEntity(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class EcodanHeatPumpThermostatEntity(EcodanHeatPumpEntity, ClimateEntity):
    """Ecodan Heat Pump climate class."""

    def __init__(
        self,
        coordinator: EcodanHeatPumpDataUpdateCoordinator,
        entity_description: ClimateEntityDescription,
    ) -> None:
        """Initialize the climate class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_temperature_unit = TEMP_CELSIUS
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
        )
        self._attr_preset_mode = PRESET_NONE

    @property
    def hvac_modes(self) -> list[str]:
        """Return the list of available hvac operation modes."""
        return [HVAC_MODE_OFF, HVAC_MODE_HEAT]

    @property
    def hvac_mode(self) -> str:
        """Return current hvac operation mode."""
        LOGGER.debug("Getting HVAC mode...")
        heat_pump_state: HeatPumpState = self.coordinator.data
        if heat_pump_state.has_power:
            if heat_pump_state.zone_operation_mode == ZONE_OPERATION_MODE_HEAT_FLOW:
                return HVAC_MODE_HEAT
            elif heat_pump_state.zone_operation_mode == ZONE_OPERATION_MODE_CURVE:
                return HVAC_MODE_AUTO
        else:
            return HVAC_MODE_OFF

    @property
    def hvac_action(self) -> str:
        """Return current hvac action."""
        LOGGER.debug("Getting HVAC action...")
        heat_pump_state: HeatPumpState = self.coordinator.data
        if heat_pump_state.has_power:
            if heat_pump_state.status == ZONE_STATUS_HEAT:
                return HVACAction.HEATING
            elif heat_pump_state.status == ZONE_STATUS_IDLE:
                return HVACAction.IDLE
            else:
                return None
        else:
            return HVACAction.OFF

    @property
    def preset_modes(self) -> list[str]:
        """Return the list of available hvac operation modes."""

        return [PRESET_NONE, PRESET_BOOST]

    @property
    def preset_mode(self) -> str:
        """Return current hvac operation mode."""
        heat_pump_state: HeatPumpState = self.coordinator.data
        if heat_pump_state.device_operation_mode == OPERATION_MODE_AUTO:
            return PRESET_NONE
        elif heat_pump_state.device_operation_mode == OPERATION_MODE_FORCE_HOT_WATER:
            return PRESET_BOOST
        else:
            return None

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        heat_pump_state: HeatPumpState = self.coordinator.data
        return heat_pump_state.flow_temperature

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        heat_pump_state: HeatPumpState = self.coordinator.data
        return heat_pump_state.target_flow_temperature

    async def async_set_temperature(self, **kwargs) -> None:
        """
        Set new target temperature.
        """
        LOGGER.debug(kwargs)
        return

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        LOGGER.debug("Setting HVAC mode...")
        return

    async def async_set_preset_mode(self, preset_mode):
        """Set new target preset mode."""
        LOGGER.debug("Setting preset mode...")
        return
