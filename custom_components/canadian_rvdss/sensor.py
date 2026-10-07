"""Sensors for Canadian RVDSS."""

from __future__ import annotations

import re
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_EPIWEEK,
    ATTR_GEO_TYPE,
    ATTR_GEO_VALUE,
    ATTR_ISSUE,
    ATTR_PERCENT_POSITIVE,
    ATTR_POSITIVE_TESTS,
    ATTR_SEASON,
    ATTR_SOURCE,
    ATTR_TESTS,
    ATTR_TIME_VALUE,
    DOMAIN,
    VIRUSES,
)
from .coordinator import RvdssCoordinator


def _normalise(value: str) -> str:
    """Normalise a column name."""
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _find_column(
    columns: list[str],
    prefixes: tuple[str, ...],
    suffix: str,
) -> str | None:
    """Find a virus column using tolerant matching."""
    normalised = {
        _normalise(column): column
        for column in columns
    }

    for prefix in prefixes:
        candidate = _normalise(prefix) + suffix

        if candidate in normalised:
            return normalised[candidate]

    for normalised_name, original in normalised.items():
        if any(
            normalised_name.startswith(_normalise(prefix))
            for prefix in prefixes
        ) and normalised_name.endswith(suffix):
            return original

    return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up RVDSS sensors."""
    coordinator: RvdssCoordinator = hass.data[DOMAIN][entry.entry_id]

    row = coordinator.data["row"]
    columns = list(row.keys())

    entities: list[CanadianRvdssSensor] = []

    for virus_id, virus in VIRUSES.items():
        pct_column = _find_column(
            columns,
            virus["prefixes"],
            "pctpositive",
        )

        if pct_column is None:
            continue

        tests_column = _find_column(
            columns,
            virus["prefixes"],
            "tests",
        )

        positive_column = _find_column(
            columns,
            virus["prefixes"],
            "positivetests",
        )

        entities.append(
            CanadianRvdssSensor(
                coordinator,
                virus_id,
                virus["name"],
                pct_column,
                tests_column,
                positive_column,
            )
        )

    async_add_entities(entities)


class CanadianRvdssSensor(
    CoordinatorEntity[RvdssCoordinator],
    SensorEntity,
):
    """Represent a Canadian RVDSS virus sensor."""

    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:virus"

    def __init__(
        self,
        coordinator: RvdssCoordinator,
        virus_id: str,
        virus_name: str,
        pct_column: str,
        tests_column: str | None,
        positive_column: str | None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        self.virus_id = virus_id
        self.virus_name = virus_name
        self.pct_column = pct_column
        self.tests_column = tests_column
        self.positive_column = positive_column

        self._attr_unique_id = (
            f"canadian_rvdss_"
            f"{coordinator.geo_type}_"
            f"{coordinator.geo_value}_"
            f"{virus_id}"
        ).lower().replace(" ", "_")

        self._attr_name = virus_name

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name=f"Canadian RVDSS - {coordinator.geo_value}",
            manufacturer="Public Health Agency of Canada",
            model="Respiratory Virus Detection Surveillance System",
            configuration_url=(
                "https://health-infobase.canada.ca/"
                "respiratory-virus-surveillance/"
            ),
        )

    @property
    def native_value(self) -> float | None:
        """Return percentage positive."""
        row = self.coordinator.data["row"]

        value = row.get(self.pct_column)

        if value in (None, "", "NA", "N/A"):
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return surveillance metadata."""
        data = self.coordinator.data
        row = data["row"]

        attributes: dict[str, Any] = {
            ATTR_EPIWEEK: row.get("epiweek"),
            ATTR_TIME_VALUE: row.get("time_value"),
            ATTR_ISSUE: row.get("issue"),
            ATTR_GEO_TYPE: row.get("geo_type"),
            ATTR_GEO_VALUE: row.get("geo_value"),
            ATTR_SEASON: data.get("season"),
            ATTR_PERCENT_POSITIVE: row.get(self.pct_column),
            ATTR_SOURCE: (
                "Public Health Agency of Canada "
                "Respiratory Virus Detection Surveillance System"
            ),
        }

        if self.tests_column:
            attributes[ATTR_TESTS] = row.get(self.tests_column)

        if self.positive_column:
            attributes[ATTR_POSITIVE_TESTS] = row.get(
                self.positive_column
            )

        return attributes
