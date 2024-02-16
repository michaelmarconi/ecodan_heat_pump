"""Switch platform for ecodan_heat_pump."""

from __future__ import annotations

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
)
from homeassistant.components.climate.const import (
    HVACAction,
    HVACMode,
    PRESET_NONE,
    PRESET_BOOST,
)
from homeassistant.const import TEMP_CELSIUS

from custom_components.ecodan_heat_pump.errors import UnrecognisedPresetModeException
from custom_components.ecodan_heat_pump.api import ApiClient
from custom_components.ecodan_heat_pump.models import (
    HeatPumpState,
    HeatingMode,
    HeatingStatus,
    ThermostatMode,
)
from custom_components.ecodan_heat_pump.const import DOMAIN, LOGGER
from custom_components.ecodan_heat_pump.coordinator import (
    Coordinator,
)
from custom_components.ecodan_heat_pump.entity import EcodanHeatPumpEntity

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
        EcodanHeatPumpClimateEntity(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class EcodanHeatPumpClimateEntity(EcodanHeatPumpEntity, ClimateEntity):
    """Ecodan Heat Pump climate class."""

    def __init__(
        self,
        coordinator: Coordinator,
        entity_description: ClimateEntityDescription,
    ) -> None:
        """Initialize the climate class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_temperature_unit = TEMP_CELSIUS
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
        )

    @property
    def hvac_modes(self) -> list[str]:
        """Return the list of available hvac operation modes."""
        return [HVACMode.OFF, HVACMode.HEAT]

    @property
    def hvac_mode(self) -> str:
        """Return current hvac operation mode."""
        LOGGER.debug("Getting HVAC mode...")
        heat_pump_state: HeatPumpState = self.coordinator.data
        if heat_pump_state.has_power:
            if heat_pump_state.thermostat_mode == ThermostatMode.FLOW_TEMPERATURE:
                return HVACMode.HEAT
            elif heat_pump_state.thermostat_mode == ThermostatMode.CURVE_TEMPERATURE:
                return HVACMode.AUTO
        else:
            return HVACMode.OFF

    @property
    def hvac_action(self) -> str:
        """Return current hvac action."""
        LOGGER.debug("Getting HVAC action...")
        heat_pump_state: HeatPumpState = self.coordinator.data
        if heat_pump_state.has_power:
            if heat_pump_state.heating_status == HeatingStatus.HEATING:
                return HVACAction.HEATING
            elif heat_pump_state.heating_status == HeatingStatus.IDLE:
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
        LOGGER.debug("Getting preset mode...")
        heat_pump_state: HeatPumpState = self.coordinator.data
        if heat_pump_state.heating_mode == HeatingMode.AUTO:
            LOGGER.debug("Preset mode is NONE")
            return PRESET_NONE
        elif heat_pump_state.heating_mode == HeatingMode.HEAT_WATER:
            LOGGER.debug("Preset mode is HEAT WATER")
            return PRESET_BOOST
        elif heat_pump_state.heating_mode == None:
            LOGGER.debug("Preset mode is NONE")
            return PRESET_NONE
        else:
            raise UnrecognisedPresetModeException(
                f"The preset mode '{heat_pump_state.heating_mode}' is not recognised!"
            )

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

    async def async_turn_on(self):
        """Turn heat pump on."""
        # TODO: nuke function?
        LOGGER.warn("Turning off?")

    async def async_turn_off(self):
        """Turn heat pump off."""
        # TODO: nuke function?
        LOGGER.warn("Turning off?")

    async def async_set_temperature(self, **kwargs) -> None:
        """
        Set new target temperature.
        """
        LOGGER.debug(kwargs)
        return

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        LOGGER.debug(f"Setting HVAC mode to '{hvac_mode}'...")
        coordinator: Coordinator = self.coordinator
        if hvac_mode == HVACMode.OFF:
            await coordinator.async_toggle_heat_pump_power(power=False)
        elif hvac_mode == HVACMode.HEAT:
            LOGGER.debug("Setting HVAC mode to 'heat'...")
            await coordinator.async_toggle_heat_pump_power(power=True)
            # await coordinator.async_set_thermostat_mode(ThermostatMode.FLOW_TEMPERATURE)
        elif hvac_mode == HVACMode.AUTO:
            LOGGER.debug("Setting HVAC mode to 'auto'...")
            await coordinator.async_toggle_heat_pump_power(power=True)
            # await coordinator.async_set_thermostat_mode(ThermostatMode.CURVE_TEMPERATURE)
        return

    async def async_set_preset_mode(self, preset_mode):
        """Set new target preset mode."""
        LOGGER.debug(f"Setting preset mode to '{preset_mode}'...")
        client: ApiClient = self.coordinator.client
        # match preset_mode:
        #     case PRESET_NONE:
        #         #

        return
