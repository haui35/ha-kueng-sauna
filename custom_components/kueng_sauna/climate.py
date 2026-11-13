"""Climate entity for Küng Sauna."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import KuengSaunaRuntimeData
from .const import (
    ACTIVE_STATES,
    MAX_HUMIDITY,
    MAX_TEMPERATURE,
    MIN_HUMIDITY,
    MIN_TEMPERATURE,
)
from .entity import KuengSaunaEntity
from .safety import start_block_reason


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Küng Sauna climate entity."""
    runtime: KuengSaunaRuntimeData = entry.runtime_data
    async_add_entities([KuengSaunaClimate(runtime.coordinator)])


class KuengSaunaClimate(KuengSaunaEntity, ClimateEntity):
    """Represent the sauna heater and its active program."""

    _attr_name = None
    _attr_translation_key = "sauna"
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_min_temp = MIN_TEMPERATURE
    _attr_max_temp = MAX_TEMPERATURE
    _attr_target_temperature_step = 1
    _attr_min_humidity = MIN_HUMIDITY
    _attr_max_humidity = MAX_HUMIDITY
    _attr_target_humidity_step = 1
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TARGET_HUMIDITY
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._unique_prefix}_climate"

    @property
    def native_current_temperature(self) -> float | None:
        return self.status.get("operation", {}).get("currTemp")

    @property
    def native_target_temperature(self) -> float | None:
        return self.status.get("operation", {}).get("targetTemp")

    @property
    def current_humidity(self) -> float | None:
        return self.status.get("operation", {}).get("currHumidity")

    @property
    def target_humidity(self) -> float | None:
        value = self.status.get("operation", {}).get("targetHumidity")
        return value if isinstance(value, (int, float)) and value >= 0 else None

    @property
    def hvac_mode(self) -> HVACMode:
        return (
            HVACMode.HEAT
            if self.status.get("state") in ACTIVE_STATES
            else HVACMode.OFF
        )

    @property
    def hvac_action(self) -> HVACAction:
        if self.hvac_mode == HVACMode.OFF:
            return HVACAction.OFF
        current = self.native_current_temperature
        target = self.native_target_temperature
        if current is not None and target is not None and current < target:
            return HVACAction.HEATING
        return HVACAction.IDLE

    @property
    def preset_modes(self) -> list[str]:
        return [str(program["name"]) for program in self.coordinator.programs]

    @property
    def preset_mode(self) -> str | None:
        operation = self.status.get("operation", {})
        if self.hvac_mode != HVACMode.OFF and operation.get("name"):
            return str(operation["name"])
        if self.coordinator.selected_program_id is None:
            return None
        selected = self.coordinator.program_by_id(self.coordinator.selected_program_id)
        return str(selected["name"]) if selected else None

    @property
    def fan_modes(self) -> list[str]:
        return ["off", "on"]

    @property
    def fan_mode(self) -> str:
        return "on" if self.status.get("fan") else "off"

    def _ensure_start_is_allowed(self) -> None:
        if reason := start_block_reason(self.status):
            raise ServiceValidationError(reason)

    async def _selected_program(self) -> dict[str, Any]:
        program_id = self.coordinator.selected_program_id
        if program_id is None:
            raise ServiceValidationError("No sauna program is selected")
        return await self.coordinator.api.async_get_program(program_id)

    async def async_turn_on(self) -> None:
        self._ensure_start_is_allowed()
        program = await self._selected_program()
        await self.coordinator.api.async_set_operation(program, enable=True)
        await self.coordinator.async_refresh_after_command()

    async def async_turn_off(self) -> None:
        operation_id = self.status.get("operation", {}).get("id")
        if isinstance(operation_id, int) and operation_id:
            program = await self.coordinator.api.async_get_program(operation_id)
        else:
            program = await self._selected_program()
        await self.coordinator.api.async_set_operation(program, enable=False)
        await self.coordinator.async_refresh_after_command()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self.async_turn_off()
        elif hvac_mode == HVACMode.HEAT:
            await self.async_turn_on()
        else:
            raise ServiceValidationError(f"Unsupported HVAC mode: {hvac_mode}")

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        program = self.coordinator.program_by_name(preset_mode)
        if program is None:
            raise ServiceValidationError(f"Unknown sauna program: {preset_mode}")
        self.coordinator.selected_program_id = int(program["id"])
        if self.hvac_mode != HVACMode.OFF:
            self._ensure_start_is_allowed()
            detail = await self.coordinator.api.async_get_program(int(program["id"]))
            await self.coordinator.api.async_set_operation(detail, enable=True)
            await self.coordinator.async_refresh_after_command()
        else:
            self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        if self.hvac_mode == HVACMode.OFF:
            raise ServiceValidationError(
                "Start the sauna before changing its target temperature"
            )
        await self.coordinator.api.async_set_temperature(float(temperature))
        await self.coordinator.async_refresh_after_command()

    async def async_set_humidity(self, humidity: int) -> None:
        if self.hvac_mode == HVACMode.OFF:
            raise ServiceValidationError(
                "Start the sauna before changing its target humidity"
            )
        await self.coordinator.api.async_set_humidity(humidity)
        await self.coordinator.async_refresh_after_command()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        if fan_mode not in self.fan_modes:
            raise ServiceValidationError(f"Unsupported fan mode: {fan_mode}")
        if self.hvac_mode == HVACMode.OFF:
            raise ServiceValidationError("Start the sauna before changing the fan")
        await self.coordinator.api.async_set_fan(fan_mode == "on")
        await self.coordinator.async_refresh_after_command()
