"""Coordinator for Canadian RVDSS."""

from __future__ import annotations

import csv
import io
import logging
from datetime import timedelta
from typing import Any

from aiohttp import ClientError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_GEO_TYPE,
    CONF_GEO_VALUE,
    CONF_SCAN_INTERVAL,
    DATA_URL_TEMPLATE,
    REPOSITORY_API_URL,
)

_LOGGER = logging.getLogger(__name__)


class RvdssCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch Canadian RVDSS data."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.entry = entry

        self.geo_type = entry.data[CONF_GEO_TYPE]
        self.geo_value = entry.data[CONF_GEO_VALUE]

        interval = entry.data.get(
            CONF_SCAN_INTERVAL,
            24,
        )

        super().__init__(
            hass,
            _LOGGER,
            name="Canadian RVDSS",
            update_interval=timedelta(hours=interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch and process RVDSS data."""
        session = async_get_clientsession(self.hass)

        try:
            async with session.get(
                REPOSITORY_API_URL,
                headers={"Accept": "application/vnd.github+json"},
            ) as response:
                if response.status != 200:
                    raise UpdateFailed(
                        "Unable to retrieve RVDSS season list: "
                        f"HTTP {response.status}"
                    )

                seasons = await response.json()

            season_names = sorted(
                (
                    item["name"]
                    for item in seasons
                    if item.get("type") == "dir"
                    and item.get("name", "").startswith("season_")
                ),
                reverse=True,
            )

            if not season_names:
                raise UpdateFailed(
                    "No RVDSS surveillance seasons were found."
                )

            for season in season_names:
                result = await self._fetch_season(
                    session,
                    season,
                )

                if result:
                    rows, selected_season = result
                    return self._process_rows(
                        rows,
                        selected_season,
                    )

            raise UpdateFailed(
                "No RVDSS data was found for "
                f"{self.geo_type}={self.geo_value}"
            )

        except UpdateFailed:
            raise

        except (ClientError, OSError, ValueError) as err:
            _LOGGER.exception(
                "Unable to retrieve RVDSS data",
            )
            raise UpdateFailed(
                f"Unable to retrieve RVDSS data: {err}"
            ) from err

    async def _fetch_season(
        self,
        session,
        season: str,
    ) -> tuple[list[dict[str, str]], str] | None:
        """Download and filter one surveillance season."""
        csv_url = DATA_URL_TEMPLATE.format(
            season=season,
        )

        try:
            async with session.get(csv_url) as response:
                if response.status != 200:
                    _LOGGER.debug(
                        "Could not retrieve %s: HTTP %s",
                        csv_url,
                        response.status,
                    )
                    return None

                text = await response.text()

        except (ClientError, OSError) as err:
            _LOGGER.debug(
                "Could not retrieve RVDSS season %s: %s",
                season,
                err,
            )
            return None

        reader = csv.DictReader(
            io.StringIO(text),
        )

        matching = [
            row
            for row in reader
            if self._matches_location(row)
        ]

        if not matching:
            return None

        return matching, season

    def _matches_location(
        self,
        row: dict[str, str],
    ) -> bool:
        """Check whether a row matches the configured geography."""
        row_geo_type = (
            row.get("geo_type") or ""
        ).strip().lower()

        row_geo_value = (
            row.get("geo_value") or ""
        ).strip().lower()

        return (
            row_geo_type == self.geo_type.strip().lower()
            and row_geo_value == self.geo_value.strip().lower()
        )

    def _process_rows(
        self,
        rows: list[dict[str, str]],
        season: str | None,
    ) -> dict[str, Any]:
        """Select the newest revision of the newest epidemiological week."""

        grouped: dict[str, dict[str, str]] = {}

        for row in rows:
            epiweek = (
                row.get("epiweek") or ""
            ).strip()

            if not epiweek:
                continue

            existing = grouped.get(epiweek)

            if existing is None:
                grouped[epiweek] = row
                continue

            old_issue = (
                existing.get("issue") or ""
            ).strip()

            new_issue = (
                row.get("issue") or ""
            ).strip()

            if new_issue > old_issue:
                grouped[epiweek] = row

        if not grouped:
            raise UpdateFailed(
                "RVDSS returned no usable observations."
            )

        latest_epiweek = max(
            grouped,
            key=self._epiweek_sort_key,
        )

        latest = grouped[latest_epiweek]

        return {
            "row": latest,
            "season": season,
            "geo_type": self.geo_type,
            "geo_value": self.geo_value,
        }

    @staticmethod
    def _epiweek_sort_key(epiweek: str) -> tuple[int, int]:
        """Sort epidemiological week values safely."""
        try:
            value = int(epiweek)
            return value // 100, value % 100
        except ValueError:
            return 0, 0