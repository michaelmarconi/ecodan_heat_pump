# Custom integration for Ecodan heat pumps

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]


This is a Home Assistant custom component that integrates
a Mitsubishi Ecodan air source heat pump.  This is a **beta** release that is applicable to my personal heat pump, so it might not work with yours, so I'm happy to review your pull request if you want to help me widen its applicability!

## Development

After opening the devcontainer, it will run the `setup` script.  After completion, run the `develop` script at the terminal and wait until you
are prompted to open the browser window.

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `ecodan_heat_pump`.
1. Download _all_ the files from the `custom_components/ecodan_heat_pump/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Ecodan Heat Pump"

