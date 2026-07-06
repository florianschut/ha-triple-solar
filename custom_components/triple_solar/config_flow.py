"""Config flow for the Triple Solar integration."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_EMAIL, CONF_ID, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.service_info.dhcp import DhcpServiceInfo

from .const import DOMAIN
from .transport import TripleSolarTransport

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ID): str,
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


def _validate_credentials_sync(email: str, password: str) -> None:
    """Synchronously attempt to connect and fetch JWT tokens.

    This function will be safely run inside Home Assistant's background thread pool.
    """
    transport = TripleSolarTransport(email=email, password=password)
    transport.connect()
    transport.close()


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    try:
        # TODO Transport should be async
        # Offload the synchronous HTTP login request to a background thread
        await hass.async_add_executor_job(
            _validate_credentials_sync, data[CONF_EMAIL], data[CONF_PASSWORD]
        )
    except Exception as err:
        # TODO there is also a CannotConnect, probaby good to filter on cause of the exception
        _LOGGER.error("Authentication check failed for %s: %s", data[CONF_EMAIL], err)
        raise InvalidAuth from err

    # TODO Add hp info the the device title
    return {"title": f"Triple Solar ({data[CONF_ID]})"}


class TripleSolarConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Triple Solar."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            # except CannotConnect:
            #     errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_dhcp(self, discovery_info: DhcpServiceInfo):
        """Handle DHCP discovery, only to detect the device, user still needs to login with cloud credentials."""
        discovered_mac = discovery_info.macaddress

        await self.async_set_unique_id(discovered_mac)
        self._abort_if_unique_id_configured()

        return await self.async_step_user()


# class CannotConnect(HomeAssistantError):
#     """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
