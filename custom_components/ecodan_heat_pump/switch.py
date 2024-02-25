"""Switch platform for ecodan_heat_pump."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription

from custom_components.ecodan_heat_pump.models import HeatPumpState

from .const import DOMAIN
from .coordinator import Coordinator
from .entity import EcodanHeatPumpEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the climate platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        [HeatPumpPowerSwitch(coordinator), HeatPumpForceHotWaterSwitch(coordinator)]
    )


class HeatPumpSwitchEntity(EcodanHeatPumpEntity, SwitchEntity):
    """Generic heat pump switch."""

    def __init__(  # noqa: D107
        self,
        unique_id: str,
        coordinator: Coordinator,
        entity_description: SwitchEntityDescription,
        is_on_function: function,  # noqa: F821
    ) -> None:
        super().__init__(coordinator)
        self._coordinator = coordinator
        self.entity_description = entity_description
        self._attr_unique_id = f"switch.{unique_id}"
        self.is_on_function = is_on_function

    @property
    def is_on(self) -> bool:
        """Return the is_on value by calling the is_on function."""
        return self.is_on_function(self._coordinator)


class HeatPumpPowerSwitch(HeatPumpSwitchEntity):
    """The power switch for the heat pump."""

    def __init__(  # noqa: D107
        self,
        coordinator: Coordinator,
    ) -> None:
        super().__init__(
            unique_id="heat_pump_power_switch",
            coordinator=coordinator,
            entity_description=SwitchEntityDescription(
                key=DOMAIN, name="Heat pump power switch", icon="mdi:power"
            ),
            is_on_function=lambda coordinator: coordinator.data.has_power,
        )

    async def async_turn_on(self, **_: any) -> None:
        """Turn on the switch."""
        coordinator: Coordinator = self.coordinator
        heat_pump_state: HeatPumpState = self.coordinator.data
        await coordinator.async_toggle_heat_pump_power(heat_pump_state.device_id, True)

    async def async_turn_off(self, **_: any) -> None:
        """Turn off the switch."""
        coordinator: Coordinator = self.coordinator
        heat_pump_state: HeatPumpState = self.coordinator.data
        await coordinator.async_toggle_heat_pump_power(heat_pump_state.device_id, False)


class HeatPumpForceHotWaterSwitch(HeatPumpSwitchEntity):
    """The switch that forces the heat pump to heat hot water."""

    def __init__(  # noqa: D107
        self,
        coordinator: Coordinator,
    ) -> None:
        super().__init__(
            unique_id="heat_pump_force_hot_water_switch",
            coordinator=coordinator,
            entity_description=SwitchEntityDescription(
                key=DOMAIN, name="Heat pump hot water switch", icon="mdi:water-boiler"
            ),
            is_on_function=lambda coordinator: coordinator.data.is_forced_to_heat_water,
        )

    async def async_turn_on(self, **_: any) -> None:
        """Turn on the switch."""
        coordinator: Coordinator = self.coordinator
        await coordinator.async_toggle_water_heating(True)

    async def async_turn_off(self, **_: any) -> None:
        """Turn off the switch."""
        coordinator: Coordinator = self.coordinator
        await coordinator.async_toggle_water_heating(False)
