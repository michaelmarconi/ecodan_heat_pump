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
from custom_components.ecodan_heat_pump.models import (
    HeatPumpState,
    HeatingMode,
    HeatingStatus,
)
from custom_components.ecodan_heat_pump.const import (
    DOMAIN,
    LOGGER,
    MAX_FLOW_TEMP,
    MIN_FLOW_TEMP,
)
from custom_components.ecodan_heat_pump.coordinator import (
    Coordinator,
)
from custom_components.ecodan_heat_pump.entity import EcodanHeatPumpEntity

ENTITY_DESCRIPTIONS = (
    ClimateEntityDescription(
        key=DOMAIN,
        name="Ecodan Heat Pump",
        icon="mdi:heat-pump-outline",
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the climate platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        HeatPumpClimateEntity(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class HeatPumpClimateEntity(EcodanHeatPumpEntity, ClimateEntity):
    """Ecodan Heat Pump climate class."""

    def __init__(
        self,
        coordinator: Coordinator,
        entity_description: ClimateEntityDescription,
    ) -> None:
        """Initialize the climate class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_min_temp = MIN_FLOW_TEMP
        self._attr_max_temp = MAX_FLOW_TEMP
        self._attr_temperature_unit = TEMP_CELSIUS
        self._attr_precision = 0.5
        self._attr_target_temperature_step = 1
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
        )

    @property
    def hvac_modes(self) -> list[str]:
        """Return the list of available hvac operation modes."""
        return [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]

    @property
    def hvac_mode(self) -> str:
        """Return current hvac operation mode."""
        heat_pump_state: HeatPumpState = self.coordinator.data
        if heat_pump_state.has_power:
            if heat_pump_state.heating_mode == HeatingMode.FLOW_TEMPERATURE:
                return HVACMode.HEAT
            elif heat_pump_state.heating_mode == HeatingMode.CURVE_TEMPERATURE:
                return HVACMode.AUTO
        else:
            return HVACMode.OFF

    @property
    def hvac_action(self) -> str:
        """Return current hvac action."""
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
        heat_pump_state: HeatPumpState = self.coordinator.data
        if heat_pump_state.is_forced_to_heat_water is False:
            return PRESET_NONE
        elif heat_pump_state.is_forced_to_heat_water is True:
            return PRESET_BOOST
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

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target flow temperature."""
        flow_temperature = kwargs["temperature"]
        LOGGER.debug(f"Setting flow temperature to '{flow_temperature}'...")
        coordinator: Coordinator = self.coordinator
        await coordinator.async_set_flow_temperature(flow_temperature)
        return

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        LOGGER.debug(f"Setting HVAC mode to '{hvac_mode}'...")
        coordinator: Coordinator = self.coordinator
        heat_pump_state: HeatPumpState = self.coordinator.data
        if hvac_mode == HVACMode.OFF:
            await coordinator.async_toggle_heat_pump_power(power=False)
        elif hvac_mode == HVACMode.HEAT:
            LOGGER.debug("Setting HVAC mode to 'heat'...")
            if heat_pump_state.has_power is False:
                await coordinator.async_toggle_heat_pump_power(power=True)
            await coordinator.async_set_heating_mode(HeatingMode.FLOW_TEMPERATURE)
        elif hvac_mode == HVACMode.AUTO:
            LOGGER.debug("Setting HVAC mode to 'auto'...")
            if heat_pump_state.has_power is False:
                await coordinator.async_toggle_heat_pump_power(power=True)
            await coordinator.async_set_heating_mode(HeatingMode.CURVE_TEMPERATURE)
        return

    async def async_set_preset_mode(self, preset_mode):
        """Set the preset mode."""
        LOGGER.debug(f"Setting preset mode to '{preset_mode}'...")
        coordinator: Coordinator = self.coordinator
        if preset_mode == PRESET_NONE:
            await coordinator.async_toggle_water_heating(False)
        elif preset_mode == PRESET_BOOST:
            await coordinator.async_toggle_water_heating(True)
        return
