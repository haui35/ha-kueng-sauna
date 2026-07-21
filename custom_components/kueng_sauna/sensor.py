"""Sensor entities for Küng Sauna."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import KuengSaunaRuntimeData
from .entity import KuengSaunaEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Küng Sauna sensors."""
    runtime: KuengSaunaRuntimeData = entry.runtime_data
    async_add_entities([KuengRemainingTimeSensor(runtime.coordinator)])


class KuengRemainingTimeSensor(KuengSaunaEntity, SensorEntity):
    """Report the remaining program time in minutes."""

    _attr_translation_key = "remaining_time"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_icon = "mdi:timer-outline"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._unique_prefix}_remaining_time"

    @property
    def native_value(self) -> int | float | None:
        value = self.status.get("remainingTime")
        return value if isinstance(value, (int, float)) else None
