import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .__init__ import DOMAIN, TripleSolarHeatPumpCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    coordinator: TripleSolarHeatPumpCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    switches = [
        TripleSolarSwitch(
            coordinator,
            "isHeatingEnabled",
            "Heating Enabled",
            "settings.spaceConditioning.isHeatingEnabled",
            "spaceConditioning",
        ),
        TripleSolarSwitch(
            coordinator,
            "isCoolingEnabled",
            "Cooling Enabled",
            "settings.spaceConditioning.isCoolingEnabled",
            "spaceConditioning",
        ),
        TripleSolarSwitch(
            coordinator,
            "isDHWEnabled",
            "DHW Enabled",
            "settings.dhw.isDHWEnabled",
            "dhw",
        ),
        TripleSolarSwitch(
            coordinator,
            "isLegionellaEnabled",
            "Legionella Prevention",
            "settings.dhw.isLegionellaEnabled",
            "dhw",
        ),
    ]
    async_add_entities(switches)


class TripleSolarSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, setting_key, name, data_path, category) -> None:
        super().__init__(coordinator)
        self.setting_key = setting_key
        self._category = category
        self._name = name
        self._data_path = data_path
        self._optimistic_state = None
        self._attr_unique_id = f"{coordinator.heatpump_id}_{setting_key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.heatpump_id)},
            "name": coordinator.device_name,
        }

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        # drill down through data path
        data = self.coordinator.data
        for part in self._data_path.split("."):
            if isinstance(data, dict):
                data = data.get(part, {})
        value = bool(data)

        # if optimistic value exists, prefer it until confirmed
        if self._optimistic_state is not None:
            if value == self._optimistic_state:
                self._optimistic_state = None  # backend confirmed it
            else:
                return self._optimistic_state

        return value

    async def async_turn_on(self, **kwargs):
        self._optimistic_state = True
        self.async_write_ha_state()  # update UI immediately
        try:
            await self.coordinator.async_set_heatpump_setting(
                self._category,
                self.setting_key,
                True,
            )
            await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error("Failed to turn on %s: %s", self._name, e)
            self._optimistic_state = None
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._optimistic_state = False
        self.async_write_ha_state()
        try:
            await self.coordinator.async_set_heatpump_setting(
                self._category,
                self.setting_key,
                False,
            )
            await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error("Failed to turn off %s: %s", self._name, e)
            self._optimistic_state = None
            self.async_write_ha_state()
