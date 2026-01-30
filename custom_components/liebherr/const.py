"""Constants for the Liebherr integration."""

from typing import Final

DOMAIN = "liebherr"

# See api recommendation
# https://developer.liebherr.com/apis/smartdevice-homeapi/#advice-for-implementation
DEFAULT_UPDATE_INTERVAL: Final[int] = 30  # in seconds
MIN_UPDATE_INTERVAL: Final[int] = 5  # in seconds
MAX_UPDATE_INTERVAL: Final[int] = 300  # in seconds, 5 minutes

URL_DOWNLOAD_APP: Final[str] = "https://smartdevice.onelink.me/OrY5/bciotarf"
URL_CONNECT_INSTRUCTIONS: Final[str] = ("https://www-assets.liebherr.com/media/bu-media/"
    "lhbu-hau/documents/smartdevicebox-network-imodels-en.pdf")

CONF_POLL_INTERVAL: Final[str] = "poll_interval"
CONF_PRESENTATION_LIGHT_AS_NUMBER: Final[str] = "presentation_light_as_number"

BRIGHTNESS_SCALE: Final[dict[str, tuple[int, int]]] = {"WPgbi 7472-20": (1, 5)}
DEFAULT_BRIGHTNESS_SCALE: Final[tuple[int, int]] = (1, 4)
