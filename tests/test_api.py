"""Contract tests for the standalone Küng API client."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).parents[1]
PACKAGE = "custom_components.kueng_sauna"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


package = types.ModuleType(PACKAGE)
package.__path__ = [str(ROOT / "custom_components" / "kueng_sauna")]
sys.modules.setdefault(PACKAGE, package)

aiohttp = types.ModuleType("aiohttp")


class ClientError(Exception):
    """Test stand-in for aiohttp.ClientError."""


class ClientTimeout:
    """Test stand-in for aiohttp.ClientTimeout."""

    def __init__(self, *, total) -> None:
        self.total = total


aiohttp.ClientError = ClientError
aiohttp.ClientSession = object
aiohttp.ClientTimeout = ClientTimeout
sys.modules.setdefault("aiohttp", aiohttp)

_load_module(
    f"{PACKAGE}.const", ROOT / "custom_components" / "kueng_sauna" / "const.py"
)
api_module = _load_module(
    f"{PACKAGE}.api", ROOT / "custom_components" / "kueng_sauna" / "api.py"
)
safety_module = _load_module(
    f"{PACKAGE}.safety", ROOT / "custom_components" / "kueng_sauna" / "safety.py"
)
KuengSaunaApi = api_module.KuengSaunaApi


class FakeResponse:
    def __init__(self, data, status: int = 200) -> None:
        self.data = data
        self.status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise ClientError(f"HTTP {self.status}")

    async def json(self, content_type=None):
        return self.data


class FakeSession:
    def __init__(self, responses) -> None:
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return FakeResponse(self.responses.pop(0))


class ApiContractTest(unittest.IsolatedAsyncioTestCase):
    async def test_status_and_program_parsing(self) -> None:
        session = FakeSession(
            [
                {"state": 0, "operation": {"currTemp": 24}},
                {"list": [{"id": 1, "name": "Finnish-80"}]},
            ]
        )
        api = KuengSaunaApi(session, "http://kueng-wellness.local/")

        status = await api.async_get_status()
        programs = await api.async_get_programs()

        self.assertEqual(0, status["state"])
        self.assertEqual("Finnish-80", programs[0]["name"])
        self.assertEqual(
            "http://kueng-wellness.local/api/1.30.2/sauna/", api.base_url
        )

    async def test_operation_payload(self) -> None:
        session = FakeSession([{"success": True}])
        api = KuengSaunaApi(session, "kueng-wellness.local")
        program = {"id": 1, "name": "Finnish-80", "properties": {}}

        await api.async_set_operation(program, enable=True)

        method, url, kwargs = session.calls[0]
        self.assertEqual("PUT", method)
        self.assertTrue(url.endswith("/sauna/operation"))
        self.assertEqual(
            {"program": program, "enable": True},
            kwargs["json"],
        )

    async def test_control_payloads_match_web_application(self) -> None:
        session = FakeSession([{}, {}, {}, {}])
        api = KuengSaunaApi(session, "kueng-wellness.local")

        await api.async_set_temperature(84.6)
        await api.async_set_humidity(41)
        await api.async_set_fan(True)
        await api.async_set_eco_mode(False)

        calls = [
            (method, url.rsplit("/", 1)[-1], kwargs["json"])
            for method, url, kwargs in session.calls
        ]
        self.assertEqual(
            [
                ("PUT", "temperature", {"targetTemp": 85}),
                ("PUT", "humidity", {"targetHumidity": 41}),
                ("PUT", "fan", {"power": True}),
                ("PUT", "ecomode", {"enable": False}),
            ],
            calls,
        )

    async def test_invalid_status_is_rejected(self) -> None:
        api = KuengSaunaApi(FakeSession([{"unexpected": True}]), "sauna.local")
        with self.assertRaises(api_module.KuengSaunaResponseError):
            await api.async_get_status()


class SafetyContractTest(unittest.TestCase):
    def test_start_allowed_only_with_all_safety_signals_clear(self) -> None:
        allowed = {
            "remoteAccessEnabled": True,
            "keyLock": False,
            "event": {"operationLock": False},
        }
        self.assertIsNone(safety_module.start_block_reason(allowed))

        for blocked in (
            {**allowed, "remoteAccessEnabled": False},
            {**allowed, "keyLock": True},
            {**allowed, "event": {"operationLock": True}},
        ):
            with self.subTest(blocked=blocked):
                self.assertIsNotNone(safety_module.start_block_reason(blocked))


if __name__ == "__main__":
    unittest.main()
