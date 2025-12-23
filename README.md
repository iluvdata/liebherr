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

> [!Warning]
> If you are upgrading from the `bhuebschen/liebherr` version, it's recommended to remove this first to avoid orphaned devices/entities.

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

## Usage
Once the integration is configured, your Liebherr devices will appear as entities in Home Assistant. You can:
- Monitor temperatures and other metrics.
- Control switches and settings via the Home Assistant UI or automations.
- Change the poll interval on the configuration

Controls will map to the following domains:
| Liebherr Control | Homeassistant Domain |
| -----------------| ---------------------|
| Ice Maker, BioFreshPlus | Select |
| Presentation Light | Light |
| SuperCool, SuperFreeze, PartyMode, NightMode | Switch|
| HydroBreeze | Fan |
| Temperature | Climate |
| `image_url` (Device) | Image |
| Bottle Timer | Not available |

### Discover New Appliances

Currently appliances added to your Liebherr account will not be automatically discovered. Once an appliance is connected to your Liebherr account (and accessible in the SmartHome app) manually reload the integration from the integration screen:

[![Open your Home Assistant instance and show an integration.](https://my.home-assistant.io/badges/integration.svg)](https://my.home-assistant.io/redirect/integration/?domain=liebherr)

and click on "Reload" on the configuration menu:

![Menu Image](https://raw.githubusercontent.com/iluvdata/liebherr/refs/heads/main/assets/menu.png)

## Update Interval

### Version 2025.10.4

Given rate limits imposed by Liebherr in the [SmartDevice Home API](https://developer.liebherr.com/apis/smartdevice-homeapi/#advice-for-implementation) the integration can only make a request to the API every 30s.  The interval between poll updates depends on the number of devices (since controls have to be requested separately for each device) and is determined by:

$$
   polling\ interval = number\ of\ devices\ ×\ 30\ seconds
$$
#### Example
If you have 4 Liebherr devices associated with your account the update interval will be $4 × 30$ seconds $= 2$ minutes. Over this two minute period each device will be updated *sequentially* at 30 second intervals:

>  Device 1 > 30 seconds > Device 2 > 30 seconds > Device 3 > 30 Seconds > Device 4 > 30 seconds > Device 1 > ...

### Version 2025.12.0

This version will calculate the polling interval based on the number of devices/appliances associated with your Liebherr account.  Essentially the goal is to poll each device's controls every 30 seconds and is calculated thusly:

```math
poll\ interval=\frac{30\ seconds}{number\ of\ devices}
```
With a minimun poll interval of 30 seconds.

## Troubleshooting
- Ensure your Liebherr api key is correct.
- Check the Home Assistant logs for any errors related to the integration.
- Enable debug on the integration.
- Download and inspect the integration diagnotics.
- If there are many `HTTP 429 - Too many requests` try increasing the polling interval.

## Acknowledgements
This is a rewrite of the great [custom intergration](https://github.com/bhuebschen/liebherr) orginally maintained by @bhuebschen from a fork created by @skatsavos.  The original intergration stopped working in Oct 2025 and the orginal maintainer did not appear to be maintaining the project.

> [!Warning]
> This is nearly a complete rewrite to the orginal integration.  As such there is not a suitable upgrade path. Start by removing the prior liebherr entry and HACS respository from your Homeassistant **before** proceeding with installation.

> [!Warning]
> This was tested on a Liebherr Device lacking:
>> - AutoDoor
>> - Presentation Light
>> - BioFreshPlus (reported to be working)
>> - HydroBreeze (reported to be working)
>
> If you encounter an issue with these features please submit an issue [here](https://github.com/iluvdata/liebherr/issues).

### Significant Changes from [bhuebschen/liebherr v0.1.1](https://github.com/bhuebschen/liebherr)
- Data is now pulled from the API using a single "coordinated" pull set on a configurable interval per https://github.com/bhuebschen/liebherr/issues/44#issuecomment-3442421338 and https://developer.liebherr.com/apis/smartdevice-homeapi/ set to a default interval of 30s.
- Added support for all the support features in the API such as IceMaker Control, BioFreshPlus, AutoDoor, Presentation Light (wine fridges) and HydroBreeze (see Caution above).
- Translation support has been greatly expanded but please note I was not able to update the many translations (please feel free to contribute)!
- Device/appliance list will only be queried upon setup.  If you add a new device to your Liebherr account you with have to "Reload" the integration in Homeassitant (or restart Homeassistant).
- The integration was modernized to align better with Homeassistant's development standards https://developers.home-assistant.io/docs/development_index and remove the use of deprecated functions.


## Support
If you encounter any issues or have feature requests, please open an issue on the [GitHub Issues page](https://github.com/iluvdata/liebherr/issues).

## Contributions
Contributions are welcome! Feel free to submit pull requests to improve this integration.

## License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/iluvdata/liebherr/blob/main/LICENSE) file for details.
