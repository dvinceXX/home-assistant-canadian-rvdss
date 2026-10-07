"""Constants for the Canadian Respiratory Virus Surveillance integration."""

from __future__ import annotations

DOMAIN = "canadian_rvdss"

CONF_GEO_TYPE = "geo_type"
CONF_GEO_VALUE = "geo_value"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_GEO_TYPE = "region"
DEFAULT_GEO_VALUE = "on"
DEFAULT_SCAN_INTERVAL = 24

REPOSITORY_API_URL = (
    "https://api.github.com/repos/dajmcdon/rvdss-canada/contents/data"
)

DATA_URL_TEMPLATE = (
    "https://raw.githubusercontent.com/"
    "dajmcdon/rvdss-canada/main/data/{season}/positive_tests.csv"
)

ATTR_EPIWEEK = "epiweek"
ATTR_TIME_VALUE = "time_value"
ATTR_ISSUE = "issue"
ATTR_GEO_TYPE = "geo_type"
ATTR_GEO_VALUE = "geo_value"
ATTR_TESTS = "tests"
ATTR_POSITIVE_TESTS = "positive_tests"
ATTR_PERCENT_POSITIVE = "percent_positive"
ATTR_SOURCE = "source"
ATTR_SEASON = "season"

SOURCE_NAME = (
    "Public Health Agency of Canada "
    "Respiratory Virus Detection Surveillance System"
)

# The RVDSS dataset does not use normal Canadian province codes
# consistently. Ontario, Quebec and British Columbia are represented
# as "region" records in the published dataset.
GEOGRAPHIES = {
    "nation": {
        "Canada": "ca",
    },
    "province": {
        "Alberta": "ab",
        "Manitoba": "mb",
        "New Brunswick": "nb",
        "Newfoundland and Labrador": "nl",
        "Nova Scotia": "ns",
        "Northwest Territories": "nt",
        "Nunavut": "nu",
        "Prince Edward Island": "pe",
        "Saskatchewan": "sk",
        "Yukon": "yt",
    },
    "region": {
        "Atlantic": "atlantic",
        "British Columbia": "bc",
        "Ontario": "on",
        "Prairies": "prairies",
        "Quebec": "qc",
        "Territories": "territories",
    },
}

GEO_TYPE_NAMES = {
    "nation": "Canada",
    "province": "Province",
    "region": "RVDSS region",
}

VIRUSES = {
    "influenza": {
        "name": "Influenza",
        "prefixes": ("flu",),
    },
    "influenza_a": {
        "name": "Influenza A",
        "prefixes": ("flua",),
    },
    "influenza_b": {
        "name": "Influenza B",
        "prefixes": ("flub",),
    },
    "sars_cov_2": {
        "name": "SARS-CoV-2",
        "prefixes": ("sarscov2",),
    },
    "rsv": {
        "name": "RSV",
        "prefixes": ("rsv",),
    },
    "parainfluenza": {
        "name": "Parainfluenza",
        "prefixes": ("hpiv",),
    },
    "adenovirus": {
        "name": "Adenovirus",
        "prefixes": ("adv",),
    },
    "metapneumovirus": {
        "name": "Human metapneumovirus",
        "prefixes": ("hmpv",),
    },
    "rhinovirus": {
        "name": "Enterovirus/Rhinovirus",
        "prefixes": ("evrv",),
    },
    "coronavirus": {
        "name": "Human coronavirus",
        "prefixes": ("hcov",),
    },
}