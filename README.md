# Liebherr Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square&logo=homeassistantcommunitystore)](https://hacs.xyz/)
![GitHub Release](https://img.shields.io/github/v/release/iluvdata/liebherr)
![Dynamic JSON Badge](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Filuvdata%2Fliebherr%2Frefs%2Fheads%2Fmain%2Fcustom_components%2Fliebherr%2Fmanifest.json&query=%24.version&prefix=v&label=dev-version&labelColor=orange)

This is a custom integration for Home Assistant that allows you to connect and control Liebherr smart devices via the Liebherr HomeAPI.

## Features
- Monitor current and target temperatures of your Liebherr fridges and freezers.
- Control device features such as switching power modes.
- View detailed information about your appliances.

## Installation

### HACS (Recommended)
1. Ensure that [HACS](https://hacs.xyz/) is installed in your Home Assistant instance.
2. Add this repository as a custom repository in HACS:
   - Open HACS in Home Assistant.
   - Go to **Integrations**.
   - Click on the three dots in the top-right corner and select **Custom repositories**.
   - Add the following URL: `https://github.com/bhuebschen/liebherr`.
   - Select **Integration** as the category.
3. Search for "Liebherr" in the HACS integrations list and install it.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=bhuebschen&repository=liebherr&category=integration)


### Manual Installation
1. Download the latest release from the [GitHub Releases page](https://github.com/bhuebschen/liebherr/releases).
2. Extract the downloaded archive.
3. Copy the `custom_components/liebherr` folder to your Home Assistant `custom_components` directory.
   - Example: `/config/custom_components/liebherr`
4. Restart Home Assistant.

## Configuration
1. In Home Assistant, navigate to **Settings** > **Devices & Services**.
2. Click **Add Integration**.
3. Search for "Liebherr" and select it.
4. Enter your Liebherr HomeAPI API key. (see [here](https://developer.liebherr.com/apis/smartdevice-homeapi/), how to get the key)
5. Complete the setup process.

## Usage
Once the integration is configured, your Liebherr devices will appear as entities in Home Assistant. You can:
- Monitor temperatures and other metrics.
- Control switches and settings via the Home Assistant UI or automations.

## Troubleshooting
- Ensure your Liebherr api key is correct.
- Check the Home Assistant logs for any errors related to the integration.

## Support
If you encounter any issues or have feature requests, please open an issue on the [GitHub Issues page](https://github.com/bhuebschen/liebherr/issues).

## Contributions
Contributions are welcome! Feel free to submit pull requests to improve this integration.

## License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/bhuebschen/liebherr/blob/main/LICENSE) file for details.
