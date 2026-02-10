"""Support for Liebherr mode switches."""

from datetime import datetime
from io import BytesIO
import logging

from PIL.Image import Image as PImage, open
from pyliebherr import LiebherrDevice

from homeassistant.components.image import (
    Image,
    ImageContentTypeError,
    ImageEntity,
    valid_image_content_type,
)
from homeassistant.core import HomeAssistant
from homeassistant.util.dt import as_utc

from .coordinator import LiebherrConfigEntry
from .entity import async_get_device_info, async_get_unique_id

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: LiebherrConfigEntry, async_add_entities
):
    """Set up Liebherr switches from a config entry."""

    async_add_entities(
        [LiebherrImage(hass, device) for device in config_entry.runtime_data.data]
    )


class LiebherrImage(ImageEntity):
    """Image of the device."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: LiebherrDevice,
    ) -> None:
        """Initialize the image entity."""
        self.has_entity_name = True
        super().__init__(hass=hass)
        self.unique_id = async_get_unique_id(device.device_id, "image")
        self._attr_device_info = async_get_device_info(device)
        self._attr_content_type = "image/png"
        self._attr_icon = "mdi:image"
        self._attr_image_url = device.image_url
        self._attr_translation_key = "device_image"

    async def _async_load_image_from_url(self, url: str) -> Image | None:
        """Load an image by url."""
        if response := await self._fetch_url(url):
            content_type = response.headers.get("content-type")
            last_modified: datetime = as_utc(
                datetime.strptime(
                    response.headers.get("last-modified"), "%a, %d %b %Y %H:%M:%S %Z"
                )
            )
            if content_type == ".png":
                content_type = "image/png"
            try:
                valid_image_content_type(content_type)
                io_image: BytesIO = BytesIO(response.content)
                image: PImage = open(
                    io_image
                )  # await self.hass.async_add_executor_job(open, io_image)
                new_pimage: PImage = image.reduce(4)
                image.close()
                new_image: BytesIO = BytesIO()
                new_pimage.save(new_image, "PNG")
                new_pimage.close()
                self._attr_image_last_updated = last_modified
                self.async_write_ha_state()
                return Image(content_type, new_image.getvalue())
            except ImageContentTypeError:
                _LOGGER.error(
                    "%s: Image from %s has invalid content type: %s",
                    self.entity_id,
                    url,
                    content_type,
                )
                return None
        return None
