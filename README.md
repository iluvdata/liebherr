# Liebherr Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square&logo=homeassistantcommunitystore)](https://hacs.xyz/)
![GitHub Release](https://img.shields.io/github/v/release/iluvdata/liebherr)
![Dynamic JSON Badge](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Filuvdata%2Fliebherr%2Frefs%2Fheads%2Fmain%2Fcustom_components%2Fliebherr%2Fmanifest.json&query=%24.version&prefix=v&label=dev-version&labelColor=orange)

This is a *unofficial* custom integration for Home Assistant that allows you to connect and control Liebherr smart devices via the Liebherr HomeAPI.  

## Acknowledgement
This is a rewrite of the great [custom intergration](https://github.com/bhuebschen/liebherr) orginally maintained by @bhuebschen from a fork created by @skatsavos.  The original intergration stopped work in Oct 2025 and the orginal maintainer did not appear to be maintaining the project.

> [!Warning]
> This is nearly a complete rewrite to the orginal integration.  As such there is not a suitable upgrade path. I'd suggest starting deleting the prior liebherr entry and HACS respository from your Homeassistant **before** proceeding with installation below.

> [!Caution]
> I only have access to a Liebherr fridge with a limited number of features.  I have not been able to test:
> - AutoDoor
> - BioFreshPlus
> - HydroBreeze
>
> If you encounter an issue with these features please submit an issue here.

## Features
- Monitor current and target temperatures of your Liebherr fridges and freezers.
- Control device features such as cooling modes and ice makers.

## Significant Changes from [bhuebschen/liebherr v0.1.1](https://github.com/bhuebschen/liebherr)
- Data is now pulled from the API using a single "coordinated" pull set on a configurable interval per https://github.com/bhuebschen/liebherr/issues/44#issuecomment-3442421338 and https://developer.liebherr.com/apis/smartdevice-homeapi/ set to a default interval of 30s.
- Added support for all the support features in the API such as IceMaker Control, BioFreshPlus, AutoDoor, Presentation Light (wine fridges) and HydroBreeze (see Caution above).
- Translation support has been greatly expanded but please note I was not able to update the many translations (please feel free to contribute)!
- Device/appliance list will only be queried upon setup.  If you add a new device to your Liebherr account you with have to "Reload" the integration in Homeassitant (or restart Homeassistant).

## Installation

### HACS (Recommended)

> [!Warning]
> Consider manually removing the prior version to avoid orphaned devices/entities.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?category=custom_respository&owner=iluvdata&repository=liebherr)

### OR

1. Ensure that [HACS](https://hacs.xyz/) is installed in your Home Assistant instance.
2. Add this repository as a custom repository in HACS:
   - Open HACS in Home Assistant.
   - Go to **Integrations**.
   - Click on the three dots in the top-right corner and select **Custom repositories**.
   - Add the following URL: `https://github.com/iluvdata/liebherr`.
   - Select **Integration** as the category.
3. Search for "Liebherr" in the HACS integrations list and install it.


### Manual Installation
1. Download the latest release from the [GitHub Releases page](https://github.com/iluvdata/liebherr/releases).
2. Extract the downloaded archive.
3. Copy the `custom_components/liebherr` folder to your Home Assistant `custom_components` directory.
   - Example: `/config/custom_components/liebherr`
4. Restart Home Assistant.

## Configuration

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=pdf_scrape)

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

## Troubleshooting
- Ensure your Liebherr api key is correct.
- Check the Home Assistant logs for any errors related to the integration.
- Enable debug on the integration.

## Support
If you encounter any issues or have feature requests, please open an issue on the [GitHub Issues page](https://github.com/iluvdata/liebherr/issues).

## Contributions
Contributions are welcome! Feel free to submit pull requests to improve this integration.

## License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/bhuebschen/liebherr/blob/main/LICENSE) file for details.
