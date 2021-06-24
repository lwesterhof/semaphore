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
"""This module contains an object that represents a Signal message queue."""
import json
import logging
from typing import AsyncIterable, Dict, Optional

from .address import Address
from .attachment import Attachment
from .data_message import DataMessage
from .group import Group
from .groupV2 import GroupV2
from .message import Message
from .message_sender import MessageSender
from .socket import Socket
from .sticker import Sticker
from .sticker_pack import StickerPack


class MessageReceiver:
    """This object represents a Signal message queue."""

    def __init__(self, socket: Socket, sender: MessageSender):
        """Initialize message receiver."""
        self._socket: Socket = socket
        self._sender: MessageSender = sender
        self.log = logging.getLogger(__name__)

    async def receive(self) -> AsyncIterable[Message]:
        """Receive messages and return as Iterator."""
        async for raw_line in self._socket.read():
            line: str = raw_line.decode()
            self.log.debug(f'Socket receive: {line}')

            # Load Signal message wrapper
            try:
                message_wrapper: Dict
                message_wrapper = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Handle Errors
            if message_wrapper.get("exception"):
                self.log.warning(f"Signald an exception for: {message_wrapper}")

            # Handle listen_stopped
            if message_wrapper["type"] == "listen_stopped":
                self.log.warning(f"Signald won't deliver new messages: {message_wrapper}")
                raise ValueError("Signald: listen stopped")

            # Only handle messages.
            if message_wrapper["type"] != "message":
                continue

            try:
                message = message_wrapper["data"]
                data_message: Optional[DataMessage] = None
                data = message.get("dataMessage")
                if data:
                    group: Optional[Group] = None
                    groupV2: Optional[GroupV2] = None
                    if data.get("group"):
                        group = Group(
                            group_id=data["group"].get("groupId"),
                            name=data["group"].get("name"),
                            group_type=data["group"].get("type"),
                        )
                    if data.get("groupV2"):
                        groupV2 = GroupV2(
                            group_id=data["groupV2"].get("id")
                        )

                    sticker_data = data.get("sticker")
                    sticker: Optional[Sticker] = None
                    if sticker_data:
                        pack = StickerPack(
                            pack_id=sticker_data["packID"],
                            pack_key=sticker_data["packKey"],
                        )
                        sticker = Sticker(
                            sticker_id=sticker_data["stickerID"],
                            pack=pack,
                        )

                    data_message = DataMessage(
                        timestamp=data["timestamp"],
                        body=data.get("body", ""),
                        expires_in_seconds=data.get("expiresInSeconds"),
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
                        groupV2=groupV2,
                        sticker=sticker,
                    )

                yield Message(
                    username=message["username"],
                    source=Address(
                        uuid=message["source"].get("uuid"),
                        number=message["source"].get("number"),
                    ),
                    envelope_type=message["type"],
                    timestamp=message["timestamp"],
                    timestamp_iso=message["timestampISO"],
                    server_timestamp=message["serverDeliveredTimestamp"],
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
                self.log.error(
                    f"Could not receive message: {json.dumps(message)}",
                    exc_info=exc,
                )
