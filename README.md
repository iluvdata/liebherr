# Liebherr Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square&logo=homeassistantcommunitystore)](https://hacs.xyz/)
![GitHub Release](https://img.shields.io/github/v/release/iluvdata/liebherr)
![Dynamic JSON Badge](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Filuvdata%2Fliebherr%2Frefs%2Fheads%2Fmain%2Fcustom_components%2Fliebherr%2Fmanifest.json&query=%24.version&prefix=v&label=dev-version&labelColor=orange)

This is an *unofficial* custom integration for Home Assistant that allows you to connect and control Liebherr smart devices via the Liebherr SmartHomeAPI using the simple [pyliebherr](https://github.com/iluvdata/pyliebherr) library.

## Features
- Monitor current and target temperatures of your Liebherr refridgeratorss and freezers.
- Control device features such as BioFreshPlus, Hydrobreeze, AutoDoor, Presentation Lights, and Ice Makers.

## Installation

### HACS (Recommended)


[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?category=integration&owner=iluvdata&repository=liebherr)

or search for the Liebherr integration in HACS

### Manual Installation
1. Download the latest release from the [GitHub Releases page](https://github.com/iluvdata/liebherr/releases).
2. Extract the downloaded archive.
3. Copy the `custom_components/liebherr` folder to your Home Assistant `custom_components` directory.
   - Example: `/config/custom_components/liebherr`
4. Restart Home Assistant.

## Configuration

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=liebherr)

### Or
1. In Home Assistant, navigate to **Settings** > **Devices & Services**.
2. Click **Add Integration**.
3. Search for "Liebherr" and select it.

### Then

1. Enter your Liebherr HomeAPI API key. (see [here](https://developer.liebherr.com/apis/smartdevice-homeapi/), how to get the key)
2. Complete the setup process.
3. (Optional):  Configure the polling interval and the entity type for Presentation Light (see below).

## Usage
Once the integration is configured, your Liebherr devices will appear as entities in Home Assistant. You can:
- Monitor temperatures and other metrics.
- Control switches and settings via the Home Assistant UI or automations.
- Change the poll interval on the configuration

Controls will map to the following domains:
| Liebherr Control | Homeassistant Domain |
| -----------------| ---------------------|
| Auto Door | Cover |
|Ice Maker, BioFreshPlus | Select |
| Presentation Light | Light or Number*|
| SuperCool, SuperFreeze, PartyMode, NightMode | Switch|
| HydroBreeze | Fan |
| Temperature | Climate |
| `image_url` (Device) | Image |
| Bottle Timer | Not available |

*\* In version ≥ 2025.12.5 the domain/type of control/entity created can be selected in the integration options.*

### Discover New Appliances

Currently appliances added to your Liebherr account will not be automatically discovered. Once an appliance is connected to your Liebherr account (and accessible in the SmartHome app) manually reload the integration from the integration screen:

[![Open your Home Assistant instance and show an integration.](https://my.home-assistant.io/badges/integration.svg)](https://my.home-assistant.io/redirect/integration/?domain=liebherr)

and click on "Reload" on the configuration menu:

![Menu Image](https://raw.githubusercontent.com/iluvdata/liebherr/refs/heads/main/assets/menu.png)

## Update Interval

Given rate limits imposed by Liebherr in the beta [SmartDevice Home API](https://developer.liebherr.com/apis/smartdevice-homeapi/#advice-for-implementation) the integration can only make a request to the device control API more often than every 30s.

> [!NOTE] Last Updated Sensor
> A diagnostic sensor will be created for each device showing the last timestamp of the most recent poll but is disabled by default (as it will quickly fill up your database with state changes).

### Version ≥ 2025.12.0

This version will calculate the polling interval based on the number of devices/appliances associated with your Liebherr account.  Essentially the goal is to poll each device's controls every 30 seconds and is calculated thusly:

```math
poll\ interval=\frac{30\ seconds}{number\ of\ devices}
```
With a minimun poll interval of 30 seconds. 

The polling interval can be adjusted manual (within some present limits) by changing the integration options.

## Troubleshooting
- Ensure your Liebherr api key is correct.
- Check the Home Assistant logs for any errors related to the integration.
- Enable debug on the integration.
- Download and inspect the integration diagnotics.
- If there are many `HTTP 429 - Too many requests` try increasing the polling interval.

## Acknowledgements
This is a rewrite of the great [custom intergration](https://github.com/bhuebschen/liebherr) orginally maintained by @bhuebschen from a fork created by @skatsavos.  The original intergration stopped working in Oct 2025 and the orginal maintainer did not appear to be maintaining the project.


> [!Warning]
> This was tested on a Liebherr Device lacking:
>> - AutoDoor
>> - Presentation Light (reported to be working as number entity and partially as a light entity)
>> - BioFreshPlus (reported to be working)
>> - HydroBreeze (reported to be working)
>
> If you encounter an issue with these features please submit an issue.

## Support
If you encounter any issues or have feature requests, please open an issue on the [GitHub Issues page](https://github.com/iluvdata/liebherr/issues).

## Contributions
Contributions are welcome! Feel free to submit pull requests to improve this integration.

## License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/iluvdata/liebherr/blob/main/LICENSE) file for details.
