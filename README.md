# Canadian Respiratory Virus Surveillance

Home Assistant custom integration for Canada's Respiratory Virus Detection
Surveillance System (RVDSS).

## Data source

Data is provided by the Public Health Agency of Canada and made available
through the `dajmcdon/rvdss-canada` data repository.

https://github.com/dajmcdon/rvdss-canada

## Installation

Install through HACS.

Add this repository as a custom HACS repository:

`https://github.com/dvinceXX/home-assistant-canadian-rvdss`

Select **Integration**.

Restart Home Assistant.

Then go to:

**Settings → Devices & services → Add integration**

Search for:

**Canadian Respiratory Virus Surveillance**

## Configuration

Choose:

- Canada
- Province
- Region

Then enter the corresponding geography.

For example:

- Geography type: `Province`
- Geography: `Ontario`

The integration checks for the latest RVDSS surveillance season
automatically.

## Sensors

Sensors are created for available respiratory viruses.

The sensor state is the percentage of tests that were positive.

Additional attributes include:

- epidemiological week
- surveillance date
- revision date
- geography
- test count
- positive test count
- surveillance season
- data source
