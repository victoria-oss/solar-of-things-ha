"""Sensor platform for Solar of Things integration."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_DEFINITIONS

_LOGGER = logging.getLogger(__name__)

# Map sensor key → translation_key (snake_case)
_TRANSLATION_KEYS: dict[str, str] = {
    "pvInputPower": "pv_input_power",
    "acOutputActivePower": "ac_output_active_power",
    "batteryDischargeCurrent": "battery_discharge_current",
    "batteryChargingCurrent": "battery_charging_current",
    "batteryVoltage": "battery_voltage",
    "batteryPower": "battery_power",
    "batteryCapacity": "battery_soc",
    "feedInPower": "feed_in_power",
    "gridPower": "grid_power",
    "loadPower": "load_power",
    "acInputVoltage": "ac_input_voltage",
    "acInputFrequency": "ac_input_frequency",
    "outputVoltage": "output_voltage",
    "outputFrequency": "output_frequency",
    "outputApparentPower": "output_apparent_power",
    "pvInputVoltage": "pv_input_voltage",
    "gridState": "grid_state",
    "mainsRelayStatus": "mains_relay_status",
    "battery_type": "battery_type",
    "max_total_charge_current": "max_total_charge_current",
    "utility_charge_current": "utility_charge_current",
    "bulk_charging_voltage": "bulk_charging_voltage",
    "float_charging_voltage": "float_charging_voltage",
    "low_voltage_shutdown": "low_voltage_shutdown",
    "battery_equalization_enabled": "battery_equalization_enabled",
    "battery_equalization_voltage": "battery_equalization_voltage",
    "battery_equalization_time": "battery_equalization_time",
    "battery_equalization_timeout": "battery_equalization_timeout",
    "battery_equalization_interval": "battery_equalization_interval",
    "ntc_maximum_temperature": "ntc_maximum_temperature",
    "working_state": "working_state",
    "battery_state": "battery_state",
    "pv_status": "pv_status",
    "output_relay_status": "output_relay_status",
    "photovoltaic_access_flag": "photovoltaic_access_flag",
    "load_status": "load_status",
    "monthly_pv_generated": "monthly_pv_generated",
    "monthly_grid_import": "monthly_grid_import",
    "monthly_total_consumption": "monthly_total_consumption",
    "monthly_solar_percentage": "monthly_solar_percentage",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Solar of Things sensors."""

    data = hass.data[DOMAIN][entry.entry_id]
    station_id: str = data["station_id"]
    device_coordinators = data["device_coordinators"]
    station_coordinator = data["station_coordinator"]

    entities: list[SensorEntity] = []

    # Per-device sensors
    for device_id, coordinator in device_coordinators.items():
        device_name = (coordinator.device_meta or {}).get("name") or device_id

        for key, definition in SENSOR_DEFINITIONS.items():
            if key.startswith("monthly_"):
                continue

            entities.append(
                SolarOfThingsDeviceSensor(
                    coordinator=coordinator,
                    station_id=station_id,
                    device_id=device_id,
                    device_name=device_name,
                    sensor_key=key,
                    sensor_definition=definition,
                )
            )

    # Station-level monthly sensors
    if station_coordinator:
        for key, definition in SENSOR_DEFINITIONS.items():
            if not key.startswith("monthly_"):
                continue

            entities.append(
                SolarOfThingsStationMonthlySensor(
                    coordinator=station_coordinator,
                    station_id=station_id,
                    sensor_key=key,
                    sensor_definition=definition,
                )
            )

    async_add_entities(entities)


class SolarOfThingsDeviceSensor(CoordinatorEntity, SensorEntity):
    """Per-device telemetry sensor.

    Reads from either coordinator.data["time_series"] (live telemetry, the
    default) or coordinator.data["settings"] (config-style values such as
    charging voltages / equalization schedule), depending on the
    sensor_definition's "source" field.
    """

    def __init__(
        self,
        coordinator,
        station_id: str,
        device_id: str,
        device_name: str,
        sensor_key: str,
        sensor_definition: dict,
    ) -> None:
        super().__init__(coordinator)

        self._station_id = station_id
        self._device_id = device_id
        self._device_name = device_name
        self._sensor_key = sensor_key
        self._sensor_definition = sensor_definition

        self._attr_has_entity_name = True
        self._attr_translation_key = _TRANSLATION_KEYS.get(sensor_key)
        # Fallback name if no translation key
        if not self._attr_translation_key:
            self._attr_name = f"{device_name} {sensor_definition['name']}"
        self._attr_unique_id = f"{DOMAIN}_{station_id}_{device_id}_{sensor_key}"
        self._attr_icon = sensor_definition.get("icon")

        if sensor_definition.get("diagnostic"):
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

        unit = sensor_definition.get("unit")
        if sensor_definition.get("value_type") == "text":
            # Text/status sensors: no device_class, unit, or state_class.
            pass
        elif unit == "W":
            self._attr_device_class = SensorDeviceClass.POWER
            self._attr_native_unit_of_measurement = UnitOfPower.WATT
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif unit == "kWh":
            self._attr_device_class = SensorDeviceClass.ENERGY
            self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        elif unit == "A":
            self._attr_device_class = SensorDeviceClass.CURRENT
            self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif unit == "V":
            self._attr_device_class = SensorDeviceClass.VOLTAGE
            self._attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif unit == "Hz":
            self._attr_device_class = SensorDeviceClass.FREQUENCY
            self._attr_native_unit_of_measurement = "Hz"
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif unit == "%":
            if "battery" in sensor_key.lower():
                self._attr_device_class = SensorDeviceClass.BATTERY
            self._attr_native_unit_of_measurement = PERCENTAGE
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif unit == "°C":
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_native_unit_of_measurement = "°C"
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif unit in ("VA", "min", "d"):
            self._attr_native_unit_of_measurement = unit
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Siseli",
            "model": (self.coordinator.data.get("device_meta") or {}).get("model") if self.coordinator.data else None,
            "via_device": (DOMAIN, self._station_id),
        }

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        source = self._sensor_definition.get("source", "time_series")

        if source == "settings":
            settings = data.get("settings") or {}
            settings_key = self._sensor_definition.get("settings_key")
            entry = settings.get(settings_key) or {}
            value_field = self._sensor_definition.get("value_field", "value")
            val = entry.get(value_field)
        elif source == "overview":
            # fetch_device_overview() returns a flat dict where each field key
            # maps to its raw value, with a companion "<key>_display" entry
            # holding the human-readable string. value_field picks between them.
            overview = data.get("overview") or {}
            overview_key = self._sensor_definition.get("overview_key")
            value_field = self._sensor_definition.get("value_field", "value")
            if value_field == "valueDisplay":
                val = overview.get(f"{overview_key}_display")
            else:
                val = overview.get(overview_key)
        else:
            ts = data.get("time_series") or {}
            val = ts.get(self._sensor_key)

        if val is None:
            return None

        if self._sensor_definition.get("value_type") == "text":
            return str(val)

        try:
            return round(float(val), 2)
        except Exception:
            return None


class SolarOfThingsStationMonthlySensor(CoordinatorEntity, SensorEntity):
    """Station-level monthly summary sensor."""

    def __init__(
        self,
        coordinator,
        station_id: str,
        sensor_key: str,
        sensor_definition: dict,
    ) -> None:
        super().__init__(coordinator)

        self._station_id = station_id
        self._sensor_key = sensor_key
        self._sensor_definition = sensor_definition

        self._attr_has_entity_name = True
        self._attr_translation_key = _TRANSLATION_KEYS.get(sensor_key)
        if not self._attr_translation_key:
            self._attr_name = f"Station {station_id} {sensor_definition['name']}"
        self._attr_unique_id = f"{DOMAIN}_{station_id}_{sensor_key}"
        self._attr_icon = sensor_definition.get("icon")

        unit = sensor_definition.get("unit")
        if unit == "kWh":
            self._attr_device_class = SensorDeviceClass.ENERGY
            self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
            self._attr_state_class = SensorStateClass.TOTAL
        elif unit == "%":
            self._attr_native_unit_of_measurement = PERCENTAGE
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._station_id)},
            "name": f"Solar Station {self._station_id}",
            "manufacturer": "Siseli",
            "model": "Station",
        }

    @property
    def native_value(self):
        monthly = (self.coordinator.data or {}).get("monthly") or {}
        val = monthly.get(self._sensor_key)
        if val is None:
            return None
        try:
            return round(float(val), 2)
        except Exception:
            return None
