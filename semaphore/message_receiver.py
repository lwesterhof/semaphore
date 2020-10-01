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
"""This module contains an object that represents a Signal message queue."""
import json
import logging
from typing import Iterator, Optional

from .attachment import Attachment
from .data_message import DataMessage
from .group import Group
from .message import Message
from .message_sender import MessageSender
from .socket import Socket


class MessageReceiver:
    """This object represents a Signal message queue."""

    def __init__(self, socket: Socket, sender: MessageSender):
        """Initialize message receiver."""
        self._socket: Socket = socket
        self._sender: MessageSender = sender
        self.log = logging.getLogger(__name__)

    def receive(self) -> Iterator[Message]:
        """Receive messages and return as Iterator."""
        for line in map(bytes.decode, self._socket.read()):
            self.log.debug(f'Socket receive: {line}')

            # Load Signal message wrapper
            try:
                message_wrapper = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Only handle messages.
            if message_wrapper["type"] != "message":
                continue

            try:
                message = message_wrapper["data"]
                data_message: Optional[DataMessage] = None
                data = message.get("dataMessage")
                if data:
                    group: Optional[Group] = None
                    if data.get("group"):
                        group = Group(
                            group_id=data["group"].get("groupId"),
                            name=data["group"].get("name"),
                            group_type=data["group"].get("type"),
                        )

                    data_message = DataMessage(
                        timestamp=data["timestamp"],
                        body=data["body"],
                        expires_in_seconds=data["expiresInSeconds"],
                        attachments=[
                            Attachment(
                                content_type=attachment["contentType"],
                                id=attachment["id"],
                                size=attachment["size"],
                                stored_filename=attachment["storedFilename"],
                                width=attachment["width"],
                                height=attachment["height"],
                            )
                            for attachment in data.get("attachments", [])
                        ],
                        group=group,
                    )

                yield Message(
                    username=message["username"],
                    source=message["source"].get("number"),
                    envelope_type=message["type"],
                    timestamp=message["timestamp"],
                    timestamp_iso=message["timestampISO"],
                    server_timestamp=message["serverTimestamp"],
                    source_device=message.get("sourceDevice"),
                    uuid=message.get("uuid"),
                    relay=message.get("relay"),
                    has_legacy_message=message.get("hasLegacyMessage"),
                    is_receipt=message.get("isReceipt"),
                    is_unidentified_sender=message.get("isUnidentifiedSender"),
                    data_message=data_message,
                    sender=self._sender,
                )
            except Exception as exc:
                self.log.debug(
                    f"Could not receive message: {json.dumps(message)}",
                    exc_info=exc,
                )
