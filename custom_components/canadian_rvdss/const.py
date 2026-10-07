"""Constants for the Canadian Respiratory Virus Surveillance integration."""

DOMAIN = "canadian_rvdss"

CONF_GEO_TYPE = "geo_type"
CONF_GEO_VALUE = "geo_value"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_GEO_TYPE = "province"
DEFAULT_GEO_VALUE = "Ontario"
DEFAULT_SCAN_INTERVAL = 24

REPOSITORY_API_URL = (
    "https://api.github.com/repos/dajmcdon/rvdss-canada/contents/data"
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

VIRUSES = {
    "influenza": {
        "name": "Influenza",
        "prefixes": ("flu", "influenza"),
    },
    "sars_cov_2": {
        "name": "SARS-CoV-2",
        "prefixes": ("sarscov2", "sars_cov_2", "covid"),
    },
    "rsv": {
        "name": "RSV",
        "prefixes": ("rsv",),
    },
    "parainfluenza": {
        "name": "Parainfluenza",
        "prefixes": ("parainfluenza", "paraflu"),
    },
    "adenovirus": {
        "name": "Adenovirus",
        "prefixes": ("adenovirus", "adeno"),
    },
    "metapneumovirus": {
        "name": "Human metapneumovirus",
        "prefixes": ("metapneumovirus", "hmpv"),
    },
    "rhinovirus": {
        "name": "Enterovirus/Rhinovirus",
        "prefixes": ("rhinovirus", "enterovirus"),
    },
    "coronavirus": {
        "name": "Human coronavirus",
        "prefixes": ("coronavirus", "hcov"),
    },
}
