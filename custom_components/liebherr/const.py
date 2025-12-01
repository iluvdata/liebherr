"""Constants for the Liebherr integration."""

from typing import Final

DOMAIN = "liebherr"

# See api recommendation https://developer.liebherr.com/apis/smartdevice-homeapi/#advice-for-implementation
DEFAULT_UPDATE_INTERVAL: Final[int] = 30  # in seconds
MIN_UPDATE_INTERVAL: Final[int] = 5  # in seconds
MAX_UPDATE_INTERVAL: Final[int] = 300  # in seconds, 5 minutes

CONF_POLL_INTERVAL: Final[str] = "poll_interval"
