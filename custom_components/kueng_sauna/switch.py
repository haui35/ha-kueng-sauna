"""Switch entities for Küng Sauna."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import KuengSaunaRuntimeData
from .const import ACTIVE_STATES
from .entity import KuengSaunaEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Küng Sauna switches."""
    runtime: KuengSaunaRuntimeData = entry.runtime_data
    async_add_entities([KuengEcoSwitch(runtime.coordinator)])


class KuengEcoSwitch(KuengSaunaEntity, SwitchEntity):
    """Control Küng Sauna eco mode."""

    _attr_translation_key = "eco_mode"
    _attr_icon = "mdi:leaf"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._unique_prefix}_eco"

    @property
    def is_on(self) -> bool:
        return bool(self.status.get("eco"))

    @property
    def available(self) -> bool:
        """Eco mode can only be changed during an active operation."""
        return super().available and self.status.get("state") in ACTIVE_STATES

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.api.async_set_eco_mode(True)
        await self.coordinator.async_refresh_after_command()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.api.async_set_eco_mode(False)
        await self.coordinator.async_refresh_after_command()
