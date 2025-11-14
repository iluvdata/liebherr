"""Constants for the Liebherr integration."""

from typing import Final

DOMAIN = "liebherr"

# See api recommendation https://developer.liebherr.com/apis/smartdevice-homeapi/#advice-for-implementation
DEFAULT_UPDATE_INTERVAL: Final[int] = 30  # in seconds
