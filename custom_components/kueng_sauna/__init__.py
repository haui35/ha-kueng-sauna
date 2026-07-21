"""Küng Sauna integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import KuengSaunaApi
from .const import PLATFORMS
from .coordinator import KuengSaunaCoordinator


@dataclass
class KuengSaunaRuntimeData:
    """Runtime data for a Küng Sauna config entry."""

    api: KuengSaunaApi
    coordinator: KuengSaunaCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Küng Sauna from a config entry."""
    api = KuengSaunaApi(async_get_clientsession(hass), entry.data[CONF_HOST])
    coordinator = KuengSaunaCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = KuengSaunaRuntimeData(api, coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Küng Sauna config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
