"""Binary sensor platform for ecodan_heat_pump."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .const import DOMAIN
from .coordinator import Coordinator
from .entity import EcodanHeatPumpEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([HeatPumpPowerBinarySensor(coordinator)])


class HeatPumpBinarySensorEntity(EcodanHeatPumpEntity, BinarySensorEntity):
    """Generic heat pump binary sensor"""

    def __init__(
        self,
        unique_id: str,
        coordinator: Coordinator,
        entity_description: BinarySensorEntityDescription,
        is_on_function: function,
    ) -> None:
        super().__init__(coordinator)
        self._coordinator = coordinator
        self.entity_description = entity_description
        self._attr_unique_id = f"sensor.{unique_id}"
        self.is_on_function = is_on_function

    @property
    def is_on(self) -> bool:
        """Return the is_on value by calling the is_on function."""
        return self.is_on_function(self._coordinator)


class HeatPumpPowerBinarySensor(HeatPumpBinarySensorEntity):
    """Heat pump power binary sensor"""

    def __init__(
        self,
        coordinator: Coordinator,
    ) -> None:
        super().__init__(
            unique_id="heat_pump_target_flow_temperature",
            coordinator=coordinator,
            entity_description=BinarySensorEntityDescription(
                key=DOMAIN,
                name="Heat pump power",
                icon="mdi:power",
                device_class=BinarySensorDeviceClass.POWER,
            ),
            is_on_function=lambda coordinator: coordinator.data.has_power,
        )
