#!/usr/bin/env python
#
# Semaphore: A simple (rule-based) bot library for Signal Private Messenger.
# Copyright (C) 2020
# Lazlo Westerhof <semaphore@lazlo.me>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains an object that represents a signald socket."""
import json
import logging
import socket
from typing import Iterator, List


class Socket:
    """This object represents a signald socket."""

    def __init__(self, username: str, socket_path: str = "/var/run/signald/signald.sock"):
        """Initialize socket."""
        self._username: str = username
        self._socket_path: str = socket_path
        self._socket: socket.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        self.log = logging.getLogger(__name__)
        self.connect()

    def connect(self) -> None:
        """Connect to the socket."""
        self._socket.connect(self._socket_path)
        self.log.info(f"Connected to socket ({self._socket_path})")
        self.send({"type": "subscribe", "username": self._username})
        self.log.info(f"Bot attempted to subscribe to +********{self._username[-3:]}")

    def read(self) -> Iterator[bytes]:
        """Read a socket, line by line."""
        buffer: List[bytes] = []
        while True:
            char = self._socket.recv(1)
            if not char:
                raise ConnectionResetError("Connection was reset")
            if char == b"\n":
                yield b"".join(buffer)
                buffer = []
            else:
                buffer.append(char)

    def send(self, message: dict) -> None:
        """Send message to socket."""
        self.log.debug(f"Socket send: {json.dumps(message)}")
        self._socket.send(json.dumps(message).encode("utf8") + b"\n")
        self._socket.recv(1024)
