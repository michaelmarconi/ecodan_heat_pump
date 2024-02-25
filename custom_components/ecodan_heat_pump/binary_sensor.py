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
    async_add_devices(
        [
            HeatPumpDefrostModeBinarySensor(coordinator),
            HeatPumpOfflineBinarySensor(coordinator),
            HeatPumpHolidayModeBinarySensor(coordinator),
            HeatPumpHeatingProhibitedModeBinarySensor(coordinator),
            HeatPumpHotWaterProhibitedModeBinarySensor(coordinator),
        ]
    )


class HeatPumpBinarySensorEntity(EcodanHeatPumpEntity, BinarySensorEntity):
    """Generic heat pump binary sensor."""

    def __init__(  # noqa: D107
        self,
        unique_id: str,
        coordinator: Coordinator,
        entity_description: BinarySensorEntityDescription,
        is_on_function: function,  # noqa: F821
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


class HeatPumpDefrostModeBinarySensor(HeatPumpBinarySensorEntity):
    """Heat pump defrost mode binary sensor."""

    def __init__(  # noqa: D107
        self,
        coordinator: Coordinator,
    ) -> None:
        super().__init__(
            unique_id="heat_pump_defrost_mode_binary_sensor",
            coordinator=coordinator,
            entity_description=BinarySensorEntityDescription(
                key=DOMAIN,
                name="Defrost mode",
                icon="mdi:snowflake-melt",
                device_class=BinarySensorDeviceClass.POWER,
            ),
            is_on_function=lambda coordinator: coordinator.data.is_defrost_mode,
        )


class HeatPumpOfflineBinarySensor(HeatPumpBinarySensorEntity):
    """Heat pump offline binary sensor."""

    def __init__(  # noqa: D107
        self,
        coordinator: Coordinator,
    ) -> None:
        super().__init__(
            unique_id="heat_pump_offline_binary_sensor",
            coordinator=coordinator,
            entity_description=BinarySensorEntityDescription(
                key=DOMAIN,
                name="Offline",
                icon="mdi:lan-disconnect",
                device_class=BinarySensorDeviceClass.POWER,
            ),
            is_on_function=lambda coordinator: coordinator.data.is_offline,
        )


class HeatPumpHolidayModeBinarySensor(HeatPumpBinarySensorEntity):
    """Heat pump holiday mode binary sensor."""

    def __init__(  # noqa: D107
        self,
        coordinator: Coordinator,
    ) -> None:
        super().__init__(
            unique_id="heat_pump_holiday_mode_binary_sensor",
            coordinator=coordinator,
            entity_description=BinarySensorEntityDescription(
                key=DOMAIN,
                name="Holiday mode",
                icon="mdi:palm-tree",
                device_class=BinarySensorDeviceClass.POWER,
            ),
            is_on_function=lambda coordinator: coordinator.data.is_holiday_mode,
        )


class HeatPumpHeatingProhibitedModeBinarySensor(HeatPumpBinarySensorEntity):
    """Heat pump heating prohibited binary sensor."""

    def __init__(  # noqa: D107
        self,
        coordinator: Coordinator,
    ) -> None:
        super().__init__(
            unique_id="heat_pump_heating_prohibited_binary_sensor",
            coordinator=coordinator,
            entity_description=BinarySensorEntityDescription(
                key=DOMAIN,
                name="Heating prohibited",
                icon="mdi:cancel",
                device_class=BinarySensorDeviceClass.POWER,
            ),
            is_on_function=lambda coordinator: coordinator.data.is_heating_prohibited,
        )


class HeatPumpHotWaterProhibitedModeBinarySensor(HeatPumpBinarySensorEntity):
    """Heat pump how water heating prohibited binary sensor."""

    def __init__(  # noqa: D107
        self,
        coordinator: Coordinator,
    ) -> None:
        super().__init__(
            unique_id="heat_pump_hot_water_prohibited_binary_sensor",
            coordinator=coordinator,
            entity_description=BinarySensorEntityDescription(
                key=DOMAIN,
                name="Hot water prohibited",
                icon="mdi:cancel",
                device_class=BinarySensorDeviceClass.POWER,
            ),
            is_on_function=lambda coordinator: coordinator.data.is_heating_water_prohibited,
        )
