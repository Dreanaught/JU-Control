"""Sample API Client."""
import logging
import asyncio
import socket
from typing import Optional
import hashlib
import aiohttp
import async_timeout
from yarl import URL

TIMEOUT = 10


_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}
BASE_URL: URL = URL("https://www.myjudo.eu/").with_path("/interface")


class JuControlApiClient:
    """This is the JU-Control client wrapper"""

    def __init__(
        self, username: str, password: str, session: aiohttp.ClientSession
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        self._session = session
        self._password_hashed = hashlib.md5(password.encode("UTF-8")).hexdigest()
        self._token = None

    async def log_in(self) -> bool:
        """Log in to remote service."""
        query = {
            "group": "register",
            "command": "login",
            "name": "login",
            "user": self._username,
            "password": self._password_hashed,
            "role": "customer",
        }

        url = BASE_URL.with_query(query)
        login_response = await self.api_wrapper("get", url)
        if login_response.get("status").upper() == "OK":
            self._token = login_response.get("token")
            _LOGGER.info("LogIn returned token: %s", self._token)
            return True
        else:
            return False

    async def async_get_data(self) -> dict:
        """Get data from the API."""
        _LOGGER.info("GetData uses token: %s", self._token)
        query = {
            "token": self._token,
            "group": "register",
            "command": "get device data",
        }
        url = BASE_URL.with_query(query)
        device_data = await self.api_wrapper("get", url)
        entity_data = self.parse_device_data(device_data)
        return entity_data

    async def async_set_title(self, value: str) -> None:
        """Get data from the API."""
        url = "https://jsonplaceholder.typicode.com/posts/1"
        await self.api_wrapper("patch", url, data={"title": value}, headers=HEADERS)

    async def api_wrapper(
        self, method: str, url: str, data: dict = {}, headers: dict = {}
    ) -> dict:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(TIMEOUT):
                if method == "get":
                    response = await self._session.get(url, headers=headers)
                    return await response.json()

                elif method == "put":
                    await self._session.put(url, headers=headers, json=data)

                elif method == "patch":
                    await self._session.patch(url, headers=headers, json=data)

                elif method == "post":
                    await self._session.post(url, headers=headers, json=data)

        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happened! - %s", exception)

    def parse_device_data(self, response_data) -> dict:
        """Parse entity data from device data"""
        return_data = dict()
        status: str = response_data.get("status")
        data = response_data.get("data")
        # fetch data from response if status ok
        if status.upper() == "OK":
            for device in data:
                serialnumber = device.get("serialnumber")
                installation_data = device.get("installation_date")
                online_status = device.get("status")
                software_version = device.get("sv")
                hardware_version = device.get("hv")
                raw_data = device.get("data")
                for entry in raw_data:
                    da = entry.get("da")
                    device_type = entry.get("dt")
                    device_sv = entry.get("sv")
                    device_hv = entry.get("hv")
                    device_data = entry.get("data")
                    valid_data = dict()
                    for k, v in device_data.items():
                        if k == "lu":
                            pass
                        elif v is None:
                            pass
                        elif v.get("st").upper() == "OK":
                            _k_it = int(k)
                            valid_data[_k_it] = v.get("data")
            # parse values from raw data
            _8: str = valid_data.get(8)
            if len(_8) == 8:
                total_water_consumed = self.split_by_two_reverse(_8)  # in liter
            _9: str = valid_data.get(9)
            if len(_9) == 8:
                total_soft_water_consumed = self.split_by_two_reverse(_9)  # in liter
            _791 = valid_data.get(791)
            if len(_791) == 66:
                _791 = _791.split(":")[1]
                regeneration_count = int(_791[62:64] + _791[60:62], base=16)
            _90 = valid_data.get(90)
            if len(_90) == 4:
                hardness_water_raw = int(_90[2:4] + _90[0:2], base=16)
            _94 = valid_data.get(94)
            # put data into entity
            return_data["body"] = total_water_consumed

        return return_data

    def split_by_two_reverse(self, string) -> int:
        reversed = string[6:8] + string[4:6] + string[2:4] + string[0:2]
        return int(reversed, base=16)
