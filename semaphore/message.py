#!/usr/bin/env python
#
# Semaphore: A simple (rule-based) bot library for Signal Private Messenger.
# Copyright (C) 2020-2021 Lazlo Westerhof <semaphore@lazlo.me>
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
from typing import Optional, TYPE_CHECKING

import attr

from .address import Address
from .data_message import DataMessage
from .reply import Reply
if TYPE_CHECKING:
    # resolve circular imports
    from .message_sender import MessageSender


@attr.s(auto_attribs=True, frozen=True)
class Message:
    """This object represents a Signal message."""

    username: str
    source: Address
    envelope_type: int
    timestamp: int
    timestamp_iso: str
    server_timestamp: int
    _sender: 'MessageSender'
    source_device: int = attr.ib(default=0)
    uuid: str = attr.ib(default=None)
    relay: str = attr.ib(default=None)
    has_legacy_message: bool = attr.ib(default=False)
    has_content: bool = attr.ib(default=False)
    is_receipt: bool = attr.ib(default=False)
    data_message: Optional[DataMessage] = attr.ib(default=None)
    is_unidentified_sender: bool = attr.ib(default=False)

    def empty(self) -> bool:
        """Check if the message is not empty."""
        if self.data_message:
            if self.data_message.body != "":
                return False
        return True

    def get_body(self):
        """Check if the message is not empty."""
        if self.empty():
            return ""
        else:
            return self.data_message.body

    def get_sticker(self):
        """Return the message's sticker if there is one."""
        return self.data_message.sticker

    def get_group_id(self) -> Optional[str]:
        """Get group id if message is a group message."""
        if self.data_message:
            if self.data_message.groupV2:
                return self.data_message.groupV2.group_id
            if self.data_message.group:
                return self.data_message.group.group_id
        return None

    async def reply(self, *args, **kwargs) -> bool:
        """Send a reply to the message.

        :param *args:    The body of the reply
        :param **kwargs: Keyword arguments of the Reply constructor

        :return: Returns whether reply was sent successfully
        :rtype: bool
        """
        return await self._sender.reply_message(self, Reply(*args, **kwargs))

    async def typing_started(self) -> None:
        """Send a typing started message."""
        await self._sender.typing_started(self)

    async def typing_stopped(self) -> None:
        """Send a typing stopped message."""
        await self._sender.typing_stopped(self)

    async def mark_read(self) -> None:
        """Mark the message as read."""
        await self._sender.mark_read(self)
