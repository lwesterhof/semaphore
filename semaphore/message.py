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
"""This module contains an object that represents a Signal message."""
from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

import attr

from .address import Address
from .data_message import DataMessage
from .reply import Reply
from .sticker import Sticker

if TYPE_CHECKING:
    from .attachment import Attachment
    from .message_sender import MessageSender
    from .link_preview import LinkPreview
    from .profile import Profile


@attr.s(auto_attribs=True)
class Message:
    """This object represents a Signal message."""

    username: str
    source: Address
    envelope_type: int
    timestamp: int
    server_timestamp: int
    _sender: MessageSender
    source_device: int = attr.ib(default=0)
    relay: str = attr.ib(default=None)
    has_legacy_message: bool = attr.ib(default=False)
    has_content: bool = attr.ib(default=False)
    data_message: Optional[DataMessage] = attr.ib(default=None)
    is_unidentified_sender: bool = attr.ib(default=False)

    def empty(self) -> bool:
        """Check if the message is not empty."""
        if self.data_message:
            if self.data_message.body != "":
                return False
        return True

    def get_body(self) -> str:
        """Check if the message is not empty."""
        if not self.empty() and self.data_message is not None:
            return self.data_message.body
        else:
            return ""

    def get_sticker(self) -> Optional[Sticker]:
        """Return the message's sticker if there is one."""
        if self.data_message is None:
            return None
        else:
            return self.data_message.sticker

    def get_group_id(self) -> Optional[str]:
        """Get group id if message is a group message."""
        if self.data_message:
            if self.data_message.groupV2:
                return self.data_message.groupV2.id
            if self.data_message.group:
                return self.data_message.group.group_id
        return None

    async def reply(self,
                    body: str,
                    attachments: List[Attachment] = [],
                    quote: bool = False,
                    reaction: bool = False,
                    mark_read: bool = True,
                    link_previews: List[LinkPreview] = []) -> bool:
        """Send a reply to the message.

        :param body:          The body of the reply
        :param attachments:   Optional attachments to the message.
        :param quote:         Indicates if reply is quoting a message.
        :param reaction:      Indicates if reply is a reaction to message.
        :param mark_read:     Indicates if message replying to should be marked read.
        :param link_previews: Optional link previews for the message.

        :return: Returns whether reply was sent successfully
        :rtype: bool
        """
        return await self._sender.reply_message(self, Reply(body, attachments,
                                                            quote, reaction,
                                                            mark_read, link_previews))

    async def typing_started(self) -> None:
        """Send a typing started message."""
        await self._sender.typing_started(self)

    async def typing_stopped(self) -> None:
        """Send a typing stopped message."""
        await self._sender.typing_stopped(self)

    async def mark_read(self) -> None:
        """Mark the message as read."""
        await self._sender.mark_read(self)

    async def get_profile(self) -> Profile:
        """Get Signal profile of message sender."""
        return await self._sender.get_profile(self)
