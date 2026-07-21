"""Pure safety checks shared by the Küng Sauna entities."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def start_block_reason(status: Mapping[str, Any]) -> str | None:
    """Return why a remote start must be refused, if anything."""
    if not status.get("remoteAccessEnabled"):
        return "Remote start is not enabled on the Küng Sauna controller"
    if status.get("keyLock"):
        return "The Küng Sauna controller is locked"
    event = status.get("event")
    if isinstance(event, Mapping) and event.get("operationLock"):
        return "The Küng Sauna controller blocks operation because of an event"
    return None
