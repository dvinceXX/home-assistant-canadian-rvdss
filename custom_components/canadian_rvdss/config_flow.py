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
    GEOGRAPHIES,
    GEO_TYPE_NAMES,
)


class CanadianRvdssConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Canadian RVDSS config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._geo_type: str | None = None

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ):
        """Select geography type."""

        if user_input is not None:
            self._geo_type = user_input[CONF_GEO_TYPE]
            return await self.async_step_geography()

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_GEO_TYPE,
                    default=DEFAULT_GEO_TYPE,
                ): vol.In(GEO_TYPE_NAMES),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )

    async def async_step_geography(
        self,
        user_input: dict | None = None,
    ):
        """Select the geography."""

        if self._geo_type is None:
            return await self.async_step_user()

        if user_input is not None:
            geo_value = user_input[CONF_GEO_VALUE]

            await self.async_set_unique_id(
                f"{self._geo_type}_{geo_value}".lower()
            )

            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=(
                    f"RVDSS - "
                    f"{self._display_name(self._geo_type, geo_value)}"
                ),
                data={
                    CONF_GEO_TYPE: self._geo_type,
                    CONF_GEO_VALUE: geo_value,
                    CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                },
            )

        locations = GEOGRAPHIES[self._geo_type]

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_GEO_VALUE,
                    default=(
                        DEFAULT_GEO_VALUE
                        if self._geo_type == DEFAULT_GEO_TYPE
                        else next(iter(locations.values()))
                    ),
                ): vol.In(
                    {
                        code: name
                        for name, code in locations.items()
                    }
                ),
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
            step_id="geography",
            data_schema=schema,
        )

    @staticmethod
    def _display_name(
        geo_type: str,
        geo_value: str,
    ) -> str:
        """Return a friendly geography name."""
        for name, value in GEOGRAPHIES[geo_type].items():
            if value == geo_value:
                return name

        return geo_value