"""Constants for the Solar of Things integration."""

DOMAIN = "solar_of_things"

# ─── Configuration keys ────────────────────────────────────────────────────────
CONF_IOT_TOKEN = "iot_token"          # legacy / advanced manual entry
CONF_STATION_ID = "station_id"
CONF_DEVICE_ID = "device_id"
CONF_TIME_ZONE = "time_zone"

# Credential-based auth (preferred)
CONF_USER_ID = "user_id"       # Siseli account / user-ID login (not email)
CONF_PASSWORD = "password"

# Runtime-stored token state (written back to config entry)
CONF_REFRESH_TOKEN = "refresh_token"
CONF_ACCESS_TOKEN_EXPIRES = "access_token_expires"   # ISO-8601 string
CONF_REFRESH_TOKEN_EXPIRES = "refresh_token_expires" # ISO-8601 string

# ─── API bases ─────────────────────────────────────────────────────────────────
# Both auth and data endpoints live on the production server solar.siseli.com.
# The portal JS bundle embeds both test/prod AppIDs; AppID rBrTRfAPXz is the
# one accepted by solar.siseli.com (confirmed by live API testing 2026-03-07).
API_BASE_URL        = "https://solar.siseli.com"         # data endpoints
API_AUTH_BASE_URL   = "https://solar.siseli.com"         # auth / login endpoints

# ─── Auth endpoints (discovered from portal JS bundle) ─────────────────────────
# The login endpoint requires IOT-Open-AppID signing (see api.py _sign_request).
API_LOGIN           = "/apis/login/account"              # POST + signed headers
API_REFRESH_TOKEN   = "/apis/login/refresh/access/token"  # POST, no token needed

# ─── IOT Open Platform app credentials (embedded in portal umi.js) ────────────
# rBrTRfAPXz is the production AppID accepted by solar.siseli.com.
# JO4DAiNeys is the test AppID (accepted only by test.solar.siseli.com).
IOT_APP_ID          = "rBrTRfAPXz"
IOT_APP_SECRET_ENC  = "I4D0KRr2339z3pQ/at91V9BpFAOe54DaTafwSm6suIQ="

# ─── Data endpoints ────────────────────────────────────────────────────────────
API_TIME_SERIES    = "/apis/deviceState/simple/attribute/keys/history/v1"
API_MONTHLY_SUMMARY = "/apis/stationOverView/stateAttributeSummary/category/yearly"
# Remote device config endpoints (discovered 2026-03-07 from live API testing).
# These accept a plain IOT-Token header (no IOT-Open-Sign) and use the device ID
# as a query parameter.  Write sends one setting key+value per call.
API_SETTINGS_GET   = "/apis/remote/device/configs/cache/get"  # ?deviceId=<id>
API_SETTINGS_SET   = "/apis/remote/device/config/write"       # ?deviceId=<id>
API_DEVICE_LIST    = "/apis/device/list"

# ─── Token refresh window ──────────────────────────────────────────────────────
# Refresh the access token this many seconds *before* its stated expiry.
# Mirrors the portal JS which refreshes when ≤300 s remain.
TOKEN_REFRESH_LEAD_SECONDS = 300  # 5 minutes

# ─── Sensor keys ───────────────────────────────────────────────────────────────
SENSOR_KEYS = [
    "pvInputPower",
    "acOutputActivePower",
    "batteryDischargeCurrent",
    "batteryChargingCurrent",
    "batteryVoltage",
    "feedInPower",
    "batteryPower",
    "batteryCapacity",
    "gridPower",
    "loadPower",
    "acInputVoltage",
    "acInputFrequency",
    "outputVoltage",
    "outputFrequency",
    "outputApparentPower",
    "pvInputVoltage",
    "gridState",
    "mainsRelayStatus",
]

SENSOR_DEFINITIONS = {
    "pvInputPower": {
        "name": "PV Input Power",
        "unit": "W",
        "device_class": "power",
        "icon": "mdi:solar-power",
    },
    "acOutputActivePower": {
        "name": "AC Output Power",
        "unit": "W",
        "device_class": "power",
        "icon": "mdi:power-plug",
    },
    "batteryDischargeCurrent": {
        "name": "Battery Discharge Current",
        "unit": "A",
        "device_class": "current",
        "icon": "mdi:battery-arrow-down",
    },
    "batteryChargingCurrent": {
        "name": "Battery Charging Current",
        "unit": "A",
        "device_class": "current",
        "icon": "mdi:battery-arrow-up",
    },
    "batteryVoltage": {
        "name": "Battery Voltage",
        "unit": "V",
        "device_class": "voltage",
        "icon": "mdi:battery",
    },
    "batteryPower": {
        "name": "Battery Power",
        "unit": "W",
        "device_class": "power",
        "icon": "mdi:battery-charging",
    },
    "batteryCapacity": {
        "name": "Battery State of Charge",
        "unit": "%",
        "device_class": "battery",
        "icon": "mdi:battery",
    },
    "feedInPower": {
        "name": "Grid Feed-in Power",
        "unit": "W",
        "device_class": "power",
        "icon": "mdi:transmission-tower-export",
    },
    "gridPower": {
        "name": "Grid Import Power",
        "unit": "W",
        "device_class": "power",
        "icon": "mdi:transmission-tower-import",
    },
    "loadPower": {
        "name": "Load Power",
        "unit": "W",
        "device_class": "power",
        "icon": "mdi:home-lightning-bolt",
    },

    # ── New live telemetry (confirmed working from debug log 2026-07-04) ──────
    "acInputVoltage": {
        "name": "AC Input Voltage",
        "unit": "V",
        "device_class": "voltage",
        "icon": "mdi:power-plug",
    },
    "acInputFrequency": {
        "name": "AC Input Frequency",
        "unit": "Hz",
        "device_class": "frequency",
        "icon": "mdi:sine-wave",
    },
    "outputVoltage": {
        "name": "Output Voltage",
        "unit": "V",
        "device_class": "voltage",
        "icon": "mdi:power-socket",
    },
    "outputFrequency": {
        "name": "Output Frequency",
        "unit": "Hz",
        "device_class": "frequency",
        "icon": "mdi:sine-wave",
    },
    "outputApparentPower": {
        "name": "Output Apparent Power",
        "unit": "VA",
        "icon": "mdi:power-plug-outline",
    },
    "pvInputVoltage": {
        "name": "PV Input Voltage",
        "unit": "V",
        "device_class": "voltage",
        "icon": "mdi:solar-power",
    },

    # ── Raw status codes (not yet decoded — shown as text) ────────────────────
    "gridState": {
        "name": "Grid State (raw code)",
        "value_type": "text",
        "icon": "mdi:transmission-tower",
        "diagnostic": True,
    },
    "mainsRelayStatus": {
        "name": "Mains Relay Status (raw code)",
        "value_type": "text",
        "icon": "mdi:electric-switch",
        "diagnostic": True,
    },

    # ── Settings-derived sensors (read from coordinator.data["settings"]) ─────
    "battery_type": {
        "name": "Battery Type",
        "value_type": "text",
        "icon": "mdi:battery-outline",
        "source": "settings",
        "settings_key": "settingBatteryType",
        "value_field": "valueDisplay",
        "diagnostic": True,
    },
    "max_total_charge_current": {
        "name": "Max Total Charge Current",
        "unit": "A",
        "device_class": "current",
        "icon": "mdi:current-ac",
        "source": "settings",
        "settings_key": "setMaxChargingCurrent",
        "value_field": "value",
        "diagnostic": True,
    },
    "utility_charge_current": {
        "name": "Utility Charge Current",
        "unit": "A",
        "device_class": "current",
        "icon": "mdi:transmission-tower-import",
        "source": "settings",
        "settings_key": "setUtilityMaxChargingCurrent",
        "value_field": "value",
        "diagnostic": True,
    },
    "bulk_charging_voltage": {
        "name": "Bulk Charging Voltage",
        "unit": "V",
        "device_class": "voltage",
        "icon": "mdi:battery-charging-high",
        "source": "settings",
        "settings_key": "setBatteryCVChargeVoltage",
        "value_field": "value",
        "diagnostic": True,
    },
    "float_charging_voltage": {
        "name": "Float Charging Voltage",
        "unit": "V",
        "device_class": "voltage",
        "icon": "mdi:battery-charging-medium",
        "source": "settings",
        "settings_key": "setBatteryFloatChargingVoltage",
        "value_field": "value",
        "diagnostic": True,
    },
    "low_voltage_shutdown": {
        "name": "Low Voltage Shutdown",
        "unit": "V",
        "device_class": "voltage",
        "icon": "mdi:battery-alert",
        "source": "settings",
        "settings_key": "LowBatteryCutOffVoltageSetting",
        "value_field": "value",
        "diagnostic": True,
    },
    "battery_equalization_enabled": {
        "name": "Battery Equalization",
        "value_type": "text",
        "icon": "mdi:battery-sync",
        "source": "settings",
        "settings_key": "batteryEqualizationSetting",
        "value_field": "valueDisplay",
        "diagnostic": True,
    },
    "battery_equalization_voltage": {
        "name": "Battery Equalization Voltage",
        "unit": "V",
        "device_class": "voltage",
        "icon": "mdi:battery-sync",
        "source": "settings",
        "settings_key": "setBatteryEqualizationVoltage",
        "value_field": "value",
        "diagnostic": True,
    },
    "battery_equalization_time": {
        "name": "Battery Equalization Time",
        "unit": "min",
        "icon": "mdi:timer-outline",
        "source": "settings",
        "settings_key": "setBatteryEqualizationTime",
        "value_field": "value",
        "diagnostic": True,
    },
    "battery_equalization_timeout": {
        "name": "Battery Equalization Timeout",
        "unit": "min",
        "icon": "mdi:timer-alert-outline",
        "source": "settings",
        "settings_key": "setBatteryEqualizationOverTime",
        "value_field": "value",
        "diagnostic": True,
    },
    "battery_equalization_interval": {
        "name": "Battery Equalization Interval",
        "unit": "d",
        "icon": "mdi:calendar-sync",
        "source": "settings",
        "settings_key": "batteryEqualizationIntervalSetting",
        "value_field": "value",
        "diagnostic": True,
    },

    # Monthly summary sensors
    "monthly_pv_generated": {
        "name": "Monthly PV Generated",
        "unit": "kWh",
        "device_class": "energy",
        "icon": "mdi:solar-power",
    },
    "monthly_grid_import": {
        "name": "Monthly Grid Import",
        "unit": "kWh",
        "device_class": "energy",
        "icon": "mdi:transmission-tower-import",
    },
    "monthly_total_consumption": {
        "name": "Monthly Total Consumption",
        "unit": "kWh",
        "device_class": "energy",
        "icon": "mdi:home-lightning-bolt",
    },
    "monthly_solar_percentage": {
        "name": "Monthly Solar Coverage",
        "unit": "%",
        "icon": "mdi:percent",
    },
}
