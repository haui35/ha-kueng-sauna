"""Constants for the Küng Sauna integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "kueng_sauna"
DEFAULT_HOST = "kueng-wellness.local"
DEFAULT_NAME = "Sauna"
API_VERSION = "1.30.2"
UPDATE_INTERVAL = timedelta(seconds=10)

PLATFORMS = ["binary_sensor", "climate", "sensor", "switch"]

STATE_OFF = 0
ACTIVE_STATES = {1, 2}

MIN_TEMPERATURE = 30
MAX_TEMPERATURE = 110
MIN_HUMIDITY = 0
MAX_HUMIDITY = 100


def normalize_host(value: str) -> str:
    """Return a bare host name or IP address from user input."""
    host = value.strip()
    if host.startswith("http://"):
        host = host[7:]
    elif host.startswith("https://"):
        host = host[8:]
    return host.rstrip("/")
