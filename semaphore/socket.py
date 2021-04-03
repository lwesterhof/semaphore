#!/usr/bin/env python
#
# Semaphore: A simple (rule-based) bot library for Signal Private Messenger.
# Copyright (C) 2020 Lazlo Westerhof <semaphore@lazlo.me>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""This module contains an object that represents a signald socket."""
import json
import logging
from typing import AsyncIterable, List

import anyio
import anyio.abc


class Socket:
    """This object represents a signald socket."""

    def __init__(self,
                 username: str,
                 socket_path: str = "/var/run/signald/signald.sock",
                 subscribe: bool = False):
        """Initialize socket."""
        self._username: str = username
        self._socket_path: str = socket_path
        self._socket: anyio.abc.SocketStream
        self._subscribe: bool = subscribe

        self.log = logging.getLogger(__name__)

    async def __aenter__(self) -> 'Socket':
        """Connect to the socket."""
        self._socket = await (await anyio.connect_unix(self._socket_path)).__aenter__()
        self.log.info(f"Connected to socket ({self._socket_path})")

        if self._subscribe:
            await self.send({"type": "subscribe", "username": self._username})
            self.log.info(f"Bot attempted to subscribe to +********{self._username[-3:]}")
        return self

    async def __aexit__(self, *excinfo):
        """Disconnect from the internal socket."""
        await self.send({"type": "unsubscribe", "username": self._username})
        self.log.info(f"Bot attempted to unsubscribe to +********{self._username[-3:]}")
        return await self._socket.__aexit__(*excinfo)

    async def read(self) -> AsyncIterable[bytes]:
        """Read a socket, line by line."""
        buffer: List[bytes] = []
        while True:
            try:
                char = await self._socket.receive(1)
            except anyio.EndOfStream:
                raise ConnectionResetError("Connection was reset")
            if char == b"\n":
                yield b"".join(buffer)
                buffer = []
            else:
                buffer.append(char)

    async def send(self, message: dict) -> None:
        """Send message to socket."""
        serialized = json.dumps(message)
        self.log.debug(f"Socket send: {serialized}")
        await self._socket.send(serialized.encode("utf8") + b"\n")
