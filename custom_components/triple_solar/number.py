import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .__init__ import DOMAIN, TripleSolarHeatPumpCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
):
    coordinator: TripleSolarHeatPumpCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    numbers = [
        TripleSolarNumber(
            coordinator,
            "autoSetpTemp",
            "DHW Auto Temp",
            "settings.dhw.autoSetpTemp",
            "dhw",
            20,
            70,
            0.1,
            UnitOfTemperature.CELSIUS,
        ),
        TripleSolarNumber(
            coordinator,
            "spaceHeatingSinkSupplySetpTemp",
            "Heating Sink Temp",
            "settings.spaceConditioning.spaceHeatingSinkSupplySetpTemp",
            "spaceConditioning",
            20,
            65,
            1,
            UnitOfTemperature.CELSIUS,
        ),
        TripleSolarNumber(
            coordinator,
            "modulationPerc",
            "DHW Modulation %",
            "settings.dhw.modulationPerc",
            "dhw",  # category
            0,
            100,
            1,
            PERCENTAGE,
        ),
    ]
    async_add_entities(numbers)


class TripleSolarNumber(CoordinatorEntity, NumberEntity):
    def __init__(
        self,
        coordinator,
        setting_key,
        name,
        data_path,
        category,
        min_value,
        max_value,
        step,
        unit,
    ) -> None:
        super().__init__(coordinator)
        self._setting_key = setting_key
        self._category = category
        self._name = name
        self._data_path = data_path
        self._optimistic_value = None  # store last user-set value
        self._attr_unique_id = f"{coordinator.heatpump_id}_{setting_key}"
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = unit
        self._attr_mode = NumberMode.BOX
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.heatpump_id)},
            "name": coordinator.device_name,
        }

    @property
    def name(self) -> str:
        return self._name

    @property
    def native_value(self) -> float:
        data = self.coordinator.data
        for part in self._data_path.split("."):
            if isinstance(data, dict):
                data = data.get(part)
        real_value = float(data) if data is not None else None

        # if we’ve set something and backend hasn’t confirmed yet, show that
        if self._optimistic_value is not None:
            if real_value == self._optimistic_value:
                self._optimistic_value = None  # confirmed
            else:
                return self._optimistic_value
        return real_value

    async def async_set_native_value(self, value: float) -> None:
        """Update the number setting and reflect it immediately."""
        self._optimistic_value = int(value)
        self.async_write_ha_state()  # show new value right away

        try:
            await self.coordinator.async_set_heatpump_setting(
                self._category,
                self._setting_key,
                int(value),
            )
            await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error("Failed to set %s to %s: %s", self._name, value, e)
            self._optimistic_value = None
            self.async_write_ha_state()
