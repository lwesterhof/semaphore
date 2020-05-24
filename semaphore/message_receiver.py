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
"""This object represents a Signal message queue."""
import json
from typing import Iterator

from .attachment import Attachment
from .data_message import DataMessage
from .group_info import GroupInfo
from .message import Message
from .socket import Socket


class MessageReceiver:
    def __init__(self, socket: Socket):
        self._socket: Socket = socket

    def receive(self) -> Iterator[Message]:
        """Receive messages and return as Iterator."""

        for line in self._socket.read():
            # Load Signal message wrapper
            try:
                message_wrapper = json.loads(line.decode())
            except json.JSONDecodeError:
                continue

            # Only handle messages.
            if message_wrapper["type"] != "message":
                continue

            message = message_wrapper["data"]

            data_message = {}
            if message.get("dataMessage"):
                data = message.get("dataMessage")

                group_info = None
                if data.get("groupInfo"):
                    group_info = GroupInfo(
                        group_id=data["groupInfo"].get("groupId"),
                        name=data["groupInfo"].get("name"),
                        group_type=data["groupInfo"].get("type"),
                    )

                data_message = DataMessage(
                    timestamp=data["timestamp"],
                    message=data["message"],
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
                    group_info=group_info,
                )

            yield Message(
                username=message["username"],
                source=message["source"],
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
            )
