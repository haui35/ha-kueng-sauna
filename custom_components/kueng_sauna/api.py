"""Async client for the local Küng Wellness sauna API."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout

from .const import API_VERSION, normalize_host


class KuengSaunaApiError(Exception):
    """Base exception for the Küng Sauna API."""


class KuengSaunaConnectionError(KuengSaunaApiError):
    """Raised when the sauna cannot be reached."""


class KuengSaunaResponseError(KuengSaunaApiError):
    """Raised when the sauna returns an invalid response."""


class KuengSaunaApi:
    """Small API client for a Küng Smart+/KS20 controller."""

    def __init__(self, session: ClientSession, host: str) -> None:
        self._session = session
        self.host = normalize_host(host)
        self.base_url = f"http://{self.host}/api/{API_VERSION}/sauna/"

    async def _request(
        self,
        method: str,
        endpoint: str,
        payload: Mapping[str, Any] | None = None,
    ) -> Any:
        """Issue a request and decode its JSON response."""
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        try:
            async with self._session.request(
                method,
                url,
                json=dict(payload) if payload is not None else None,
                headers={"Accept": "application/json"},
                timeout=ClientTimeout(total=10),
            ) as response:
                response.raise_for_status()
                if response.status == 204:
                    return None
                return await response.json(content_type=None)
        except (TimeoutError, ClientError) as err:
            raise KuengSaunaConnectionError(
                f"Unable to communicate with Küng Sauna at {self.host}"
            ) from err
        except (ValueError, TypeError) as err:
            raise KuengSaunaResponseError(
                f"Invalid response from Küng Sauna at {self.host}"
            ) from err

    async def async_get_status(self) -> dict[str, Any]:
        """Return the live controller status."""
        data = await self._request("GET", "status")
        if not isinstance(data, dict) or "state" not in data:
            raise KuengSaunaResponseError("Status response is missing required fields")
        return data

    async def async_get_programs(self) -> list[dict[str, Any]]:
        """Return the available sauna programs."""
        data = await self._request("GET", "program")
        programs = data.get("list") if isinstance(data, dict) else None
        if not isinstance(programs, list):
            raise KuengSaunaResponseError("Program response is missing its list")
        return [program for program in programs if isinstance(program, dict)]

    async def async_get_program(self, program_id: int) -> dict[str, Any]:
        """Return the full definition of one sauna program."""
        data = await self._request("GET", f"program/{program_id}")
        if not isinstance(data, dict):
            raise KuengSaunaResponseError("Program detail response is invalid")
        return data

    async def async_get_default_program(self) -> dict[str, Any]:
        """Return the controller's editable default program."""
        data = await self._request("GET", "program/default")
        if not isinstance(data, dict):
            raise KuengSaunaResponseError("Default program response is invalid")
        return data

    async def async_get_system_information(self) -> dict[str, Any]:
        """Return non-live controller metadata."""
        data = await self._request("GET", "information/system")
        return data if isinstance(data, dict) else {}

    async def async_set_operation(
        self, program: Mapping[str, Any], *, enable: bool
    ) -> Any:
        """Start or stop a full sauna program."""
        return await self._request(
            "PUT", "operation", {"program": dict(program), "enable": enable}
        )

    async def async_set_temperature(self, temperature: float) -> Any:
        """Set the active program's target temperature."""
        return await self._request(
            "PUT", "temperature", {"targetTemp": round(temperature)}
        )

    async def async_set_humidity(self, humidity: int) -> Any:
        """Set the active program's target humidity."""
        return await self._request(
            "PUT", "humidity", {"targetHumidity": round(humidity)}
        )

    async def async_set_fan(self, enabled: bool) -> Any:
        """Set the fan state."""
        return await self._request("PUT", "fan", {"power": enabled})

    async def async_set_eco_mode(self, enabled: bool) -> Any:
        """Set eco mode."""
        return await self._request("PUT", "ecomode", {"enable": enabled})
