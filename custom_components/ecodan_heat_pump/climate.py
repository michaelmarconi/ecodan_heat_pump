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
    PRESET_NONE,
    PRESET_BOOST,
)
from homeassistant.const import TEMP_CELSIUS

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
        return [HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_AUTO]

    @property
    def preset_mode(self) -> str:
        """Return current hvac operation mode."""
        return self._attr_preset_mode

    @property
    def preset_modes(self) -> list[str]:
        """Return the list of available hvac operation modes."""
        return [PRESET_NONE, PRESET_BOOST]

    @property
    def hvac_mode(self) -> str:
        """Return current hvac operation mode."""
        return HVAC_MODE_HEAT

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return 33

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return 36

    async def async_set_temperature(self, **kwargs) -> None:
        """
        Set new target temperature.
        """
        LOGGER.debug(kwargs)
        # self.target_temperature =
        return

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        LOGGER.debug("Setting HVAC mode...")
        self._attr_hvac_mode = hvac_mode
        return

    async def async_set_preset_mode(self, preset_mode):
        """Set new target preset mode."""
        LOGGER.debug("Setting preset mode...")
        self.preset_mode == preset_mode
        return
