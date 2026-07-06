"""Platform for sensor integration."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .__init__ import DOMAIN, TripleSolarHeatPumpCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: TripleSolarHeatPumpCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    sensors = [
        # Space Conditioning
        TripleSolarSensor(
            coordinator,
            "roomTemp",
            "Room Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            "controller.spaceConditioning.roomTemp",
        ),
        TripleSolarSensor(
            coordinator,
            "roomSetpTemp",
            "Room Setpoint Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            "controller.spaceConditioning.roomSetpTemp",
        ),
        # Domestic Hot Water
        TripleSolarSensor(
            coordinator,
            "dhwTankTemp",
            "DHW Tank Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            "controller.domesticHotWater.tankTemp",
        ),
        # Heat Pump Module Sensors
        TripleSolarSensor(
            coordinator,
            "sourceReturnTemp",
            "Source Return Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            "heatPumpModule.sensors.sourceReturnTemp",
        ),
        TripleSolarSensor(
            coordinator,
            "sourceSupplyTemp",
            "Source Supply Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            "heatPumpModule.sensors.sourceSupplyTemp",
        ),
        TripleSolarSensor(
            coordinator,
            "sinkReturnTemp",
            "Sink Return Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            "heatPumpModule.sensors.sinkReturnTemp",
        ),
        TripleSolarSensor(
            coordinator,
            "sinkSupplyTemp",
            "Sink Supply Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            "heatPumpModule.sensors.sinkSupplyTemp",
        ),
        TripleSolarSensor(
            coordinator,
            "sinkPumpFlow",
            "Sink Pump Flow",
            "L/h",
            SensorDeviceClass.VOLUME_FLOW_RATE,
            SensorStateClass.MEASUREMENT,
            "heatPumpModule.sensors.sinkPumpFlow",
        ),
        TripleSolarSensor(
            coordinator,
            "sourcePumpFlow",
            "Source Pump Flow",
            "L/h",
            SensorDeviceClass.VOLUME_FLOW_RATE,
            SensorStateClass.MEASUREMENT,
            "heatPumpModule.sensors.sourcePumpFlow",
        ),
        # Pressures
        TripleSolarSensor(
            coordinator,
            "sinkPressure",
            "Sink Pressure",
            "bar",
            SensorDeviceClass.PRESSURE,
            SensorStateClass.MEASUREMENT,
            "pressures.sink",
        ),
        TripleSolarSensor(
            coordinator,
            "sourcePressure",
            "Source Pressure",
            "bar",
            SensorDeviceClass.PRESSURE,
            SensorStateClass.MEASUREMENT,
            "pressures.source",
        ),
    ]
    # for sensor in sensors:
    #     sensor.entity_id = f"sensor.{coordinator.heatpump_id}_{sensor._key}"
    async_add_entities(sensors)


class TripleSolarSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Triple Solar Heat Pump sensor."""

    def __init__(
        self,
        coordinator: TripleSolarHeatPumpCoordinator,
        key: str,
        name: str,
        unit: str,
        device_class: SensorDeviceClass,
        state_class: SensorStateClass,
        data_path: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._name = name
        self._unit = unit
        self._device_class = device_class
        self._state_class = state_class
        self._data_path = data_path
        self._attr_unique_id = f"{coordinator.heatpump_id}_{key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.heatpump_id)},
            "name": coordinator.device_name,
            "manufacturer": "Triple Solar",
            "model": "PVT Heat Pump",
            "sw_version": self.coordinator.data.get("firmwareVersion", {}).get(
                "version", "Unknown"
            ),
            "model_id": {coordinator.heatpump_id},
        }

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._unit

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def state_class(self) -> SensorStateClass:
        """Return the state class of the sensor."""
        return self._state_class

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data
        # Navigate through the data path to get the value
        path_parts = self._data_path.split(".")
        value = data
        for part in path_parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                _LOGGER.debug(
                    "Data path %s not found for sensor %s. Current value: %s, looking for part: %s",
                    self._data_path,
                    self._name,
                    value,
                    part,
                )
                return None
        return value

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success and self.native_value is not None
