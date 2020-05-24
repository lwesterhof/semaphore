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
import json
import socket
from typing import Iterator


class Socket:
    """This object represents a signald socket."""
    def __init__(self, username, socket_path="/var/run/signald/signald.sock"):
        self._username: str = username
        self._socket_path: str = socket_path
        self._socket: socket.socket = None

        self.connect()

    def connect(self):
        """Create a socket and connect to it."""
        signald = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        signald.connect(self._socket_path)
        signald.send(json.dumps({"type": "subscribe",
                                 "username": self._username}).encode("utf8") + b"\n")
        self._socket = signald

    def read(self) -> Iterator[bytes]:
        """Read a socket, line by line."""
        buffer = []
        while True:
            char = self._socket.recv(1)
            if not char:
                raise ConnectionResetError("Connection was reset")
            if char == b"\n":
                yield b"".join(buffer)
                buffer = []
            else:
                buffer.append(char)

    def send(self, message: dict):
        """Send message to socket."""
        self._socket.send(json.dumps(message).encode("utf8") + b"\n")
        self._socket.recv(1024)
