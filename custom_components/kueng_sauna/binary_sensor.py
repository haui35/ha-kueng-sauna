"""Binary sensors for Küng Sauna."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import KuengSaunaRuntimeData
from .entity import KuengSaunaEntity


@dataclass(frozen=True, kw_only=True)
class KuengBinarySensorDescription(BinarySensorEntityDescription):
    """Describe a diagnostic binary sensor."""

    value_fn: Callable[[dict[str, Any]], bool]


DESCRIPTIONS = (
    KuengBinarySensorDescription(
        key="remote_access",
        translation_key="remote_access",
        value_fn=lambda status: bool(status.get("remoteAccessEnabled")),
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    KuengBinarySensorDescription(
        key="key_lock",
        translation_key="key_lock",
        value_fn=lambda status: bool(status.get("keyLock")),
    ),
    KuengBinarySensorDescription(
        key="operation_lock",
        translation_key="operation_lock",
        value_fn=lambda status: bool(
            status.get("event", {}).get("operationLock")
        ),
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    KuengBinarySensorDescription(
        key="event",
        translation_key="event",
        value_fn=lambda status: bool(status.get("event", {}).get("state")),
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Küng Sauna diagnostic sensors."""
    runtime: KuengSaunaRuntimeData = entry.runtime_data
    async_add_entities(
        KuengBinarySensor(runtime.coordinator, description)
        for description in DESCRIPTIONS
    )


class KuengBinarySensor(KuengSaunaEntity, BinarySensorEntity):
    """Represent one diagnostic signal."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, description: KuengBinarySensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self._unique_prefix}_{description.key}"

    @property
    def is_on(self) -> bool:
        return self.entity_description.value_fn(self.status)
