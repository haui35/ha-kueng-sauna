"""Data coordinator for the Küng Sauna integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import KuengSaunaApi, KuengSaunaApiError
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class KuengSaunaCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate polling and cached metadata for one sauna."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: KuengSaunaApi,
    ) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=UPDATE_INTERVAL,
            always_update=False,
        )
        self.api = api
        self.programs: list[dict[str, Any]] = []
        self.system_information: dict[str, Any] = {}
        self.selected_program_id: int | None = None

    async def _async_setup(self) -> None:
        """Load metadata that changes infrequently."""
        try:
            self.programs = await self.api.async_get_programs()
            self.system_information = await self.api.async_get_system_information()
        except KuengSaunaApiError as err:
            raise UpdateFailed(str(err)) from err

        favorite = next(
            (program for program in self.programs if program.get("favorite")), None
        )
        selected = favorite or (self.programs[0] if self.programs else None)
        if selected is not None:
            self.selected_program_id = int(selected["id"])

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the current state."""
        try:
            return await self.api.async_get_status()
        except KuengSaunaApiError as err:
            raise UpdateFailed(str(err)) from err

    async def async_refresh_after_command(self) -> None:
        """Refresh immediately after a state-changing command."""
        await self.async_request_refresh()

    def program_by_name(self, name: str) -> dict[str, Any] | None:
        """Find a cached program by name."""
        return next(
            (program for program in self.programs if program.get("name") == name), None
        )

    def program_by_id(self, program_id: int) -> dict[str, Any] | None:
        """Find a cached program by numeric identifier."""
        return next(
            (
                program
                for program in self.programs
                if int(program.get("id", -1)) == program_id
            ),
            None,
        )
