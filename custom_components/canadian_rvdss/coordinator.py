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
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_GEO_TYPE,
    CONF_GEO_VALUE,
    CONF_SCAN_INTERVAL,
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

        interval = entry.data.get(CONF_SCAN_INTERVAL, 24)

        super().__init__(
            hass,
            _LOGGER,
            name="Canadian RVDSS",
            update_interval=timedelta(hours=interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch and process RVDSS data."""
        try:
            async with self.hass.helpers.aiohttp.async_get_clientsession().get(
                REPOSITORY_API_URL,
                headers={"Accept": "application/vnd.github+json"},
            ) as response:
                if response.status != 200:
                    raise UpdateFailed(
                        f"GitHub repository lookup failed: HTTP {response.status}"
                    )

                seasons = await response.json()

            season_names = [
                item["name"]
                for item in seasons
                if item.get("type") == "dir"
                and item["name"].startswith("season_")
            ]

            if not season_names:
                raise UpdateFailed("No RVDSS seasons found.")

            season_names.sort(reverse=True)

            session = (
                self.hass.helpers.aiohttp.async_get_clientsession()
            )

            rows: list[dict[str, str]] = []
            selected_season = None

            for season in season_names:
                csv_url = (
                    "https://raw.githubusercontent.com/"
                    "dajmcdon/rvdss-canada/main/data/"
                    f"{season}/positive_tests.csv"
                )

                async with session.get(csv_url) as response:
                    if response.status != 200:
                        continue

                    text = await response.text()

                reader = csv.DictReader(io.StringIO(text))

                season_rows = list(reader)

                matching = [
                    row
                    for row in season_rows
                    if self._matches_location(row)
                ]

                if matching:
                    rows = matching
                    selected_season = season
                    break

            if not rows:
                raise UpdateFailed(
                    f"No RVDSS data found for "
                    f"{self.geo_type}={self.geo_value}"
                )

            return self._process_rows(rows, selected_season)

        except (ClientError, OSError, ValueError) as err:
            raise UpdateFailed(
                f"Unable to retrieve RVDSS data: {err}"
            ) from err

    def _matches_location(self, row: dict[str, str]) -> bool:
        """Check whether a row matches the configured geography."""
        row_geo_type = (row.get("geo_type") or "").strip().lower()
        row_geo_value = (row.get("geo_value") or "").strip().lower()

        wanted_type = self.geo_type.strip().lower()
        wanted_value = self.geo_value.strip().lower()

        return (
            row_geo_type == wanted_type
            and row_geo_value == wanted_value
        )

    def _process_rows(
        self,
        rows: list[dict[str, str]],
        season: str | None,
    ) -> dict[str, Any]:
        """Select the latest revision for each epidemiological week."""
        grouped: dict[str, dict[str, str]] = {}

        for row in rows:
            epiweek = (row.get("epiweek") or "").strip()

            if not epiweek:
                continue

            existing = grouped.get(epiweek)

            if existing is None:
                grouped[epiweek] = row
                continue

            old_issue = existing.get("issue", "")
            new_issue = row.get("issue", "")

            if new_issue >= old_issue:
                grouped[epiweek] = row

        if not grouped:
            raise UpdateFailed("RVDSS returned no usable observations.")

        latest_epiweek = max(grouped)
        latest = grouped[latest_epiweek]

        return {
            "row": latest,
            "season": season,
            "geo_type": self.geo_type,
            "geo_value": self.geo_value,
        }
