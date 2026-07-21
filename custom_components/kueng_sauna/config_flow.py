"""Config flow for Küng Sauna."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import KuengSaunaApi, KuengSaunaApiError
from .const import DEFAULT_HOST, DEFAULT_NAME, DOMAIN, normalize_host


async def _validate_host(hass: HomeAssistant, host: str) -> None:
    """Verify that the host answers like a Küng Sauna controller."""
    api = KuengSaunaApi(async_get_clientsession(hass), host)
    await api.async_get_status()
    await api.async_get_programs()


class KuengSaunaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a Küng Sauna config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = normalize_host(user_input[CONF_HOST])
            if not host or "/" in host:
                errors["base"] = "invalid_host"
            else:
                await self.async_set_unique_id(host.lower())
                self._abort_if_unique_id_configured()
                try:
                    await _validate_host(self.hass, host)
                except KuengSaunaApiError:
                    errors["base"] = "cannot_connect"
                except Exception:  # noqa: BLE001
                    errors["base"] = "unknown"
                else:
                    return self.async_create_entry(
                        title=DEFAULT_NAME,
                        data={CONF_HOST: host},
                    )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_HOST,
                    default=(user_input or {}).get(CONF_HOST, DEFAULT_HOST),
                ): str
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )
