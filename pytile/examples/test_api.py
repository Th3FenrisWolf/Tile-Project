"""Run an example script to quickly test."""
import asyncio
import logging

from aiohttp import ClientSession
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pytile'))
from api import async_login
from errors import TileError

_LOGGER = logging.getLogger(__name__)

TILE_EMAIL = "ralbrecht@cedarville.edu"
TILE_PASSWORD = "3lcBy5j9V21wgWf"


async def main():
    """Run."""
    logging.basicConfig(level=logging.INFO)
    async with ClientSession() as session:
        try:
            api = await async_login(TILE_EMAIL, TILE_PASSWORD, session)

            tiles = await api.async_get_tiles()
            _LOGGER.info("Tile Count: %s", len(tiles))
            for tile in tiles.values():
                _LOGGER.info("UUID: %s", tile.uuid)
                _LOGGER.info("Name: %s", tile.name)
                _LOGGER.info("Type: %s", tile.kind)
                _LOGGER.info("Latitude: %s", tile.latitude)
                _LOGGER.info("Longitude: %s", tile.longitude)
                _LOGGER.info("Last Timestamp: %s", tile.last_timestamp)
                _LOGGER.info("Auth Key: %s", tile.auth_key)
        except TileError as err:
            _LOGGER.info(err)


asyncio.run(main())
