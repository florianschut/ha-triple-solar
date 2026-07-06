import logging

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TripleSolarHeatPumpCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Set up Triple Solar Select entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    selects = [
        TripleSolarSelect(
            coordinator,
            "profile",
            "DHW Profile",
            "settings.dhw.profile",
            "dhw",
            ["Economy", "Normal", "Comfort"],
        )
    ]

    async_add_entities(selects)


class TripleSolarSelect(CoordinatorEntity, SelectEntity):
    """A dropdown selection entity for the Heat Pump."""

    def __init__(
        self, coordinator, setting_key, name, data_path, category, options
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._setting_key = setting_key
        self._category = category
        self._data_path = data_path

        # Entity Metadata
        self._attr_name = name
        self._attr_options = options
        self._attr_unique_id = f"{coordinator.heatpump_id}_{setting_key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.heatpump_id)},
            "name": coordinator.device_name,
        }

        self._option_to_api = {opt: opt.upper() for opt in options}
        self._api_to_option = {v: k for k, v in self._option_to_api.items()}

    @property
    def current_option(self) -> str | None:
        """Return the current selected option from data."""
        data = self.coordinator.data
        for part in self._data_path.split("."):
            if isinstance(data, dict):
                data = data.get(part)

        # Map "ECO" back to "Eco" for the UI
        return self._api_to_option.get(data)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        api_value = self._option_to_api[option]

        try:
            await self.coordinator.async_set_heatpump_setting(
                self._category,
                self._setting_key,
                api_value,
            )

            self.coordinator.data["settings"]["dhw"]["profile"] = api_value
            self.async_write_ha_state()

        except Exception as e:
            _LOGGER.error("Could not set %s to %s: %s", self._attr_name, option, e)
