"""Shared entity support for Küng Sauna."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import KuengSaunaCoordinator


class KuengSaunaEntity(CoordinatorEntity[KuengSaunaCoordinator]):
    """Base class for entities belonging to one sauna controller."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: KuengSaunaCoordinator) -> None:
        super().__init__(coordinator)
        system = coordinator.system_information
        serial = str(system.get("serialNumber") or coordinator.api.host)
        versions = system.get("swVersions") or {}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            name="Küng Sauna",
            manufacturer="Küng Wellness",
            model="Smart+ / KS20",
            serial_number=(
                str(system["serialNumber"]) if system.get("serialNumber") else None
            ),
            sw_version=(
                str(versions.get("hmi")) if versions.get("hmi") is not None else None
            ),
            configuration_url=f"http://{coordinator.api.host}/",
        )
        self._unique_prefix = serial

    @property
    def status(self) -> dict[str, Any]:
        """Return the latest status payload."""
        return self.coordinator.data or {}
