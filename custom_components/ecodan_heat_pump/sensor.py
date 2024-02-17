"""Sensor platform for ecodan_heat_pump."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfTemperature,
)

from custom_components.ecodan_heat_pump.const import DOMAIN
from custom_components.ecodan_heat_pump.coordinator import Coordinator
from custom_components.ecodan_heat_pump.entity import EcodanHeatPumpEntity


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            HeatPumpSensorEntity(
                unique_id="heat_pump_target_flow_temperature",
                coordinator=coordinator,
                entity_description=SensorEntityDescription(
                    key=DOMAIN,
                    name="Heat pump target flow temperature",
                    icon="mdi:thermometer",
                    device_class=SensorDeviceClass.TEMPERATURE,
                    state_class=SensorStateClass.MEASUREMENT,
                    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                    suggested_display_precision=0,
                ),
                value_function=lambda coordinator: coordinator.data.target_flow_temperature,
            ),
            HeatPumpSensorEntity(
                unique_id="heat_pump_flow_temperature",
                coordinator=coordinator,
                entity_description=SensorEntityDescription(
                    key=DOMAIN,
                    name="Heat pump flow temperature",
                    icon="mdi:thermometer-high",
                    device_class=SensorDeviceClass.TEMPERATURE,
                    state_class=SensorStateClass.MEASUREMENT,
                    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                    suggested_display_precision=0,
                ),
                value_function=lambda coordinator: coordinator.data.flow_temperature,
            ),
            HeatPumpSensorEntity(
                unique_id="heat_pump_return_temperature",
                coordinator=coordinator,
                entity_description=SensorEntityDescription(
                    key=DOMAIN,
                    name="Heat pump return temperature",
                    icon="mdi:thermometer-low",
                    device_class=SensorDeviceClass.TEMPERATURE,
                    state_class=SensorStateClass.MEASUREMENT,
                    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                    suggested_display_precision=0,
                ),
                value_function=lambda coordinator: coordinator.data.return_temperature,
            ),
            HeatPumpSensorEntity(
                unique_id="heat_pump_target_water_tank_temperature",
                coordinator=coordinator,
                entity_description=SensorEntityDescription(
                    key=DOMAIN,
                    name="Heat pump target water tank temperature",
                    icon="mdi:thermometer-water",
                    device_class=SensorDeviceClass.TEMPERATURE,
                    state_class=SensorStateClass.MEASUREMENT,
                    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                    suggested_display_precision=0,
                ),
                value_function=lambda coordinator: coordinator.data.target_water_tank_temperature,
            ),
            HeatPumpSensorEntity(
                unique_id="heat_pump_water_tank_temperature",
                coordinator=coordinator,
                entity_description=SensorEntityDescription(
                    key=DOMAIN,
                    name="Heat pump water tank temperature",
                    icon="mdi:thermometer-water",
                    device_class=SensorDeviceClass.TEMPERATURE,
                    state_class=SensorStateClass.MEASUREMENT,
                    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                    suggested_display_precision=0,
                ),
                value_function=lambda coordinator: coordinator.data.water_tank_temperature,
            ),
            HeatPumpSensorEntity(
                unique_id="heat_pump_outdoor_temperature",
                coordinator=coordinator,
                entity_description=SensorEntityDescription(
                    key=DOMAIN,
                    name="Heat pump outdoor temperature",
                    icon="mdi:home-thermometer-outline",
                    device_class=SensorDeviceClass.TEMPERATURE,
                    state_class=SensorStateClass.MEASUREMENT,
                    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                    suggested_display_precision=0,
                ),
                value_function=lambda coordinator: coordinator.data.outdoor_temperature,
            ),
        ]
    )


class HeatPumpSensorEntity(EcodanHeatPumpEntity, SensorEntity):
    """Generic heat pump temperature sensor"""

    def __init__(
        self,
        unique_id: str,
        coordinator: Coordinator,
        entity_description: SensorEntityDescription,
        value_function: function,
    ) -> None:
        super().__init__(coordinator)
        self._coordinator = coordinator
        self.entity_description = entity_description
        self._attr_unique_id = f"sensor.{unique_id}"
        self.value_function = value_function

    @property
    def native_value(self) -> str:
        """Return the temperature value by calling the value function."""
        return self.value_function(self._coordinator)
