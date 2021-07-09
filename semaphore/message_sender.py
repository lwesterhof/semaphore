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
"""This module contains a class that handles sending bot messages."""
import asyncio
import json
import logging
import re
from typing import Any, Dict

from .message import Message
from .reply import Reply
from .socket import Socket


class MessageSender:
    """This class handles sending bot messages."""
    signald_message_id: int = 0

    def __init__(self, username: str, socket: Socket):
        """Initialize message sender."""
        self._username: str = username
        self._socket: Socket = socket
        self._socket_lock = asyncio.Lock()
        self.log = logging.getLogger(__name__)

    async def _send(self, message: Dict) -> bool:
        if message['type'] == 'send':
            self.signald_message_id += 1
            message['id'] = str(self.signald_message_id)

        async with self._socket_lock:
            await self._socket.send(message)
            if not message.get('id'):
                return True

            self.log.debug(f"Waiting for success of {message['id']}")

            # Wait for success response
            async for line in self._socket.read():
                self.log.debug(f"Socket of sender received: {line.decode()}")

                # Load Signal message wrapper
                try:
                    response_wrapper = json.loads(line)
                except json.JSONDecodeError as e:
                    self.log.error("Could not decode signald response", exc_info=e)
                    continue

                # Skip everything but response for our message
                if 'id' not in response_wrapper:
                    continue

                if response_wrapper['id'] != message['id']:
                    self.log.warning("Received message response for another id")
                    continue

                if response_wrapper.get("error") is not None:
                    self.log.warning(f"Could not send message:"
                                     f"{response_wrapper}")
                    return False

                response = response_wrapper['data']
                results = response.get("results")

                if results:
                    if results[0].get('success'):
                        return True
                return False
            return False

    async def send_message(self, receiver, body, attachments=None) -> bool:
        """
        Send a message.

        :param receiver:    The receiver of the message (uuid or number).
        :param body:        The body of the message.
        :param attachments: Optional attachments to the message.

        :return: Returns whether sending is successful.
        :rtype: bool
        """
        bot_message = {
            "type": "send",
            "version": "v1",
            "username": self._username,
            "messageBody": body
        }

        if receiver[-1] == "=":
            bot_message["recipientGroupId"] = receiver
        elif re.search(r"\+\d*", receiver):
            bot_message["recipientAddress"] = {"number": receiver}
        else:
            bot_message["recipientAddress"] = {"uuid": receiver}

        # Add attachments to message.
        if attachments:
            bot_message["attachments"] = attachments

        return await self._send(bot_message)

    async def reply_message(self, message: Message, reply: Reply) -> bool:
        """
        Send the bot message.

        :param message: The original message replying to.
        :param reply:   The reply to send.


        :return: Returns whether replying is successful.
        :rtype: bool
        """
        # Mark message as read before replying.
        if reply.mark_read:
            await message.mark_read()

        # Construct reply message.
        bot_message: Dict[str, Any] = {}
        if reply.reaction:
            bot_message = {
                "type": "react",
                "version": "v1",
                "username": self._username,
                "reaction": {
                    "emoji": reply.body,
                    "targetAuthor": {"uuid": message.source.uuid},
                    "targetSentTimestamp": message.timestamp
                }
            }
        else:
            bot_message = {
                "type": "send",
                "version": "v1",
                "username": self._username,
                "messageBody": reply.body
            }

            # Add attachments to message.
            if reply.attachments:
                bot_message["attachments"] = reply.attachments

            # Add quote to message.
            if reply.quote:
                quote = {"id": message.timestamp,
                         "author": {'uuid': message.source.uuid},
                         "text": message.get_body()}
                bot_message["quote"] = quote

        # Add message recipient.
        if message.get_group_id():
            bot_message["recipientGroupId"] = message.get_group_id()
        else:
            bot_message["recipientAddress"] = {"uuid": message.source.uuid}

        return await self._send(bot_message)

    async def typing_started(self, message: Message) -> None:
        """
        Send a typing started message.

        :param message: The Signal message you received.
        """
        # Construct reply message.
        typing_message: Dict[str, Any] = {"type": "typing",
                                          "version": "v1",
                                          "typing": True,
                                          "account": self._username}

        # Add group id or address.
        if message.get_group_id():
            typing_message["group"] = message.get_group_id()
        else:
            typing_message["address"] = {"uuid": message.source.uuid}

        await self._send(typing_message)

    async def typing_stopped(self, message: Message) -> None:
        """
        Send a typing stopped message.

        :param message: The Signal message you received.
        """
        # Construct reply message.
        typing_message: Dict[str, Any] = {"type": "typing",
                                          "version": "v1",
                                          "typing": False,
                                          "account": self._username}

        # Add group id or address.
        if message.get_group_id():
            typing_message["group"] = message.get_group_id()
        else:
            typing_message["address"] = {"uuid": message.source.uuid}

        await self._send(typing_message)

    async def mark_read(self, message: Message) -> None:
        """
        Mark a Signal message you received as read.

        :param message: The Signal message you received.
        """
        await self._send({
            "type": "mark_read",
            "version": "v1",
            "account": self._username,
            "to": {"uuid": message.source.uuid},
            "timestamps": [message.timestamp],
        })

    async def set_profile(self, profile_name: str, profile_avatar: str = None) -> None:
        """
        Set Signal profile.

        :param profile_name:   New profile name, empty string for no profile name.
        :param profile_avatar: Path to profile avatar file.
        """
        profile_message = {"type": "set_profile",
                           "version": "v1",
                           "account": self._username,
                           "name": profile_name}

        if profile_avatar:
            profile_message["avatarFile"] = profile_avatar

        await self._send(profile_message)
