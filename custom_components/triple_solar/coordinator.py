"""Manages fetching data from the Triple Solar API."""

from datetime import timedelta
import logging

from gql import Client

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .graphql import HEAT_PUMP_STATUS_QUERY, UPDATE_HEAT_PUMP_SETTINGS_MUTATION
from .transport import TripleSolarTransport

_LOGGER = logging.getLogger(__name__)


class TripleSolarHeatPumpCoordinator(DataUpdateCoordinator):
    """Coordinator for managing Triple Solar heat pump data and settings.

    This coordinator handles fetching heat pump status data from the Triple Solar API
    and updating heat pump settings via GraphQL mutations.
    """

    async def async_set_heatpump_setting(self, category: str, setting_key: str, value):
        """Update a heat pump setting via GraphQL mutation."""
        settings = {category: {setting_key: value}}

        # Add required parameters with defaults
        variables = {
            "id": self.heatpump_id,
            "settings": settings,
            "advanced": False,
            "isExpert": False,
        }

        try:
            _LOGGER.debug(
                "Setting %s.%s to %s with variables: %s",
                category,
                setting_key,
                value,
                variables,
            )
            result = await self.hass.async_add_executor_job(
                self.client.execute, UPDATE_HEAT_PUMP_SETTINGS_MUTATION, variables
            )
            _LOGGER.debug(
                "Successfully updated %s.%s to %s. Result: %s",
                category,
                setting_key,
                value,
                result,
            )
            # Refresh data after setting change
            await self.async_request_refresh()
        except Exception as err:
            _LOGGER.error(
                "Error updating setting %s.%s: %s", category, setting_key, err
            )
            raise

    def __init__(
        self, hass: HomeAssistant, email: str, password: str, heatpump_id: str
    ) -> None:
        """Initialize the Triple Solar heat pump coordinator.

        Args:
            hass: Home Assistant instance.
            email: Email for Triple Solar API authentication.
            password: Password for Triple Solar API authentication.
            heatpump_id: Heat pump ID.
        """
        self.heatpump_id = heatpump_id
        self.device_name = None
        self.transport = TripleSolarTransport(email=email, password=password)
        self.client = Client(transport=self.transport)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=420),  # Update every 7 minutes
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            result = await self.hass.async_add_executor_job(
                self.client.execute,
                HEAT_PUMP_STATUS_QUERY,
                {
                    "id": self.heatpump_id,
                    "includeStatistics": False,
                    "isAdmin": False,
                    "refresh": False,
                },
            )
            if not result or "heatPump" not in result:
                raise UpdateFailed(
                    "No data returned or invalid response from Triple Solar API."
                )

            heat_pump_data = result["heatPump"]

            # Store the device name from API
            if self.device_name is None:
                self.device_name = heat_pump_data.get(
                    "name", f"Triple Solar Heat Pump ({self.heatpump_id})"
                )

            _LOGGER.debug("Successfully fetched data: %s", heat_pump_data)
            return heat_pump_data
        except Exception as err:
            _LOGGER.error("Error fetching data from Triple Solar API: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err
