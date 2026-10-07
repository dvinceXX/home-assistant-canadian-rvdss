"""Config flow for Canadian Respiratory Virus Surveillance."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import (
    CONF_GEO_TYPE,
    CONF_GEO_VALUE,
    CONF_SCAN_INTERVAL,
    DEFAULT_GEO_TYPE,
    DEFAULT_GEO_VALUE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


class CanadianRvdssConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Canadian RVDSS config flow."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ):
        """Handle the initial setup."""
        if user_input is not None:
            geo_type = user_input[CONF_GEO_TYPE]
            geo_value = user_input[CONF_GEO_VALUE]

            await self.async_set_unique_id(
                f"{geo_type}_{geo_value}".lower()
            )

            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"RVDSS - {geo_value}",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_GEO_TYPE,
                    default=DEFAULT_GEO_TYPE,
                ): vol.In(
                    {
                        "nation": "Canada",
                        "province": "Province",
                        "region": "Region",
                    }
                ),
                vol.Required(
                    CONF_GEO_VALUE,
                    default=DEFAULT_GEO_VALUE,
                ): str,
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=DEFAULT_SCAN_INTERVAL,
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=1, max=168),
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )
