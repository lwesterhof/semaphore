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
"""This module contains a class that handles sending bot messages."""
from typing import Any, Dict

from .message import Message
from .reply import Reply
from .socket import Socket


class MessageSender:
    """This class handles sending bot messages."""

    def __init__(self, username: str, socket: Socket):
        """Initialize message sender."""
        self._username: str = username
        self._socket: Socket = socket

    async def _send(self, message: Dict) -> None:
        await self._socket.send(message)

    async def send_message(self, message: Message, reply: Reply) -> None:
        """
        Send the bot message.

        :param message: The original message replying to.
        :param reply:   The reply to send.
        """
        # Mark message as read before replying.
        if reply.mark_read:
            await message.mark_read()

        # Construct reply message.
        bot_message: Dict[str, Any] = {"type": "react",
                                       "username": self._username}

        # Add message recipient.
        if message.get_group_id():
            bot_message["recipientGroupId"] = message.get_group_id()
        else:
            bot_message["recipientAddress"] = {"number": message.source}

        if reply.reaction:
            bot_message["type"] = "react"
            bot_message["reaction"] = {"emoji": reply.body,
                                       "targetAuthor": {"number": message.source},
                                       "targetSentTimestamp": message.timestamp}
        else:
            bot_message["type"] = "send"
            bot_message["messageBody"] = reply.body

        # Add attachments to message.
        if reply.attachments:
            bot_message["attachments"] = reply.attachments

        # Add quote to message.
        if reply.quote:
            quote = {"id": message.timestamp,
                     "author": message.source,
                     "text": message.get_body()}
            bot_message["quote"] = quote

        await self._send(bot_message)

    async def typing_started(self, message: Message) -> None:
        """
        Send a typing started message.

        :param message: The Signal message you received.
        """
        # Construct reply message.
        typing_message: Dict[str, Any] = {"type": "typing_started",
                                          "username": self._username,
                                          "recipientAddress": {"number": message.source}}

        # Add group id.
        if message.get_group_id():
            typing_message["recipientGroupId"] = message.get_group_id()

        await self._send(typing_message)

    async def typing_stopped(self, message: Message) -> None:
        """
        Send a typing stopped message.

        :param message: The Signal message you received.
        """
        # Construct reply message.
        typing_message: Dict[str, Any] = {"type": "typing_stopped",
                                          "username": self._username,
                                          "recipientAddress": {"number": message.source}}

        # Add group id.
        if message.get_group_id():
            typing_message["recipientGroupId"] = message.get_group_id()

        await self._send(typing_message)

    async def mark_delivered(self, message: Message) -> None:
        """
        Mark a Signal message you received as delivered.

        :param message: The Signal message you received.
        """
        await self._send({
            "type": "mark_delivered",
            "username": self._username,
            "recipientAddress": {"number": message.source},
            "timestamps": [message.timestamp],
        })

    async def mark_read(self, message: Message) -> None:
        """
        Mark a Signal message you received as read.

        :param message: The Signal message you received.
        """
        await self._send({
            "type": "mark_read",
            "username": self._username,
            "recipientAddress": {"number": message.source},
            "timestamps": [message.timestamp],
        })
