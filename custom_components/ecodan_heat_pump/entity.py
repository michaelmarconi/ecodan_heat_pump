"""BlueprintEntity class."""

from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.ecodan_heat_pump.const import DOMAIN, NAME, VERSION
from custom_components.ecodan_heat_pump.coordinator import (
    Coordinator,
)


class EcodanHeatPumpEntity(CoordinatorEntity):
    """Ecodan Heat Pump entity class."""

    def __init__(self, coordinator: Coordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=NAME,
            model=VERSION,
            manufacturer=NAME,
        )
