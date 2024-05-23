#!/usr/bin/env python
#
# Semaphore: A simple (rule-based) bot library for Signal Private Messenger.
# Copyright (C) 2020-2023 Lazlo Westerhof <semaphore@lazlo.me>
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
from __future__ import annotations

import json
import logging
from typing import AsyncIterable, Dict, Optional, TYPE_CHECKING

from .address import Address
from .attachment import Attachment
from .data_message import DataMessage
from .group import Group
from .groupV2 import GroupV2
from .link_preview import LinkPreview
from .mention import Mention
from .message import Message
from .quoted_message import QuotedMessage
from .sticker import Sticker
from .sticker_pack import StickerPack


if TYPE_CHECKING:
    from .message_sender import MessageSender
    from .socket import Socket


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
            if message_wrapper["type"] == "ListenerState":
                data = message_wrapper.get("data")
                if data and not data.get("connected"):
                    self.log.warning(f"Signald won't deliver new messages: "
                                     f"{message_wrapper}")
                    raise ValueError("Signald: listen stopped")

            # Only handle messages.
            if message_wrapper["type"] != "IncomingMessage":
                continue

            try:
                message = message_wrapper["data"]
                data_message: Optional[DataMessage] = None
                data = message.get("data_message")
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
                        groupV2 = GroupV2.create_from_receive_dict(data["groupV2"])

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
                            Attachment.create_from_receive_dict(attachment)
                            for attachment in data.get("attachments", [])
                        ],
                        mentions=[
                            Mention.create_from_receive_dict(mention)
                            for mention in data.get("mentions", [])
                        ],
                        previews=[
                            LinkPreview.create_from_receive_dict(link_preview)
                            for link_preview in data.get("previews", [])
                        ],
                        group=group,
                        groupV2=groupV2,
                        sticker=sticker,
                    )

                quoted_message: Optional[Message] = None
                quote = message.get("quote")
                if quote:
                    quoted_message = QuotedMessage.create_from_receive_dict(quote)
                yield Message(
                    username=message["account"],
                    source=Address.create_from_receive_dict(message["source"]),
                    envelope_type=message["type"],
                    timestamp=message["timestamp"],
                    server_timestamp=message["server_receiver_timestamp"],
                    source_device=message.get("source_device"),
                    relay=message.get("relay"),
                    has_legacy_message=message.get("has_legacy_message"),
                    is_unidentified_sender=message.get("unidentified_sender"),
                    data_message=data_message,
                    sender=self._sender,
                    quoted_message=quoted_message,
                )
            except Exception as exc:
                self.log.error(
                    f"Could not receive message: {json.dumps(message)}",
                    exc_info=exc,
                )
