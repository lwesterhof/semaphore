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
"""This module contains an object that represents a Signal Private Messenger bot."""
import logging
import re
import threading
from datetime import datetime
from typing import (
    Any, Awaitable, Callable, Dict, List, Match, Optional, Pattern, TYPE_CHECKING, Union
)

import anyio

from .attachment import Attachment
from .chat_context import ChatContext
from .exceptions import StopPropagation
from .groupV2 import GroupV2
from .job_queue import JobQueue
from .link_preview import LinkPreview
from .message import Message
from .message_receiver import MessageReceiver
from .message_sender import MessageSender
from .socket import Socket


class Bot:
    """This object represents a simple (rule-based) Signal Private Messenger bot."""

    def __init__(self,
                 username: str,
                 profile_name: Optional[str] = None,
                 profile_picture: Optional[str] = None,
                 profile_emoji: Optional[str] = None,
                 profile_about: Optional[str] = None,
                 group_auto_accept: bool = True,
                 logging_level: int = logging.INFO,
                 socket_path: Optional[str] = None,
                 raise_errors: bool = False) -> None:
        """Initialize bot."""
        self._username: str = username
        self._profile_name: Optional[str] = profile_name
        self._profile_picture: Optional[str] = profile_picture
        self._profile_emoji: Optional[str] = profile_emoji
        self._profile_about: Optional[str] = profile_about
        self._group_auto_accept: bool = group_auto_accept
        self._socket_path: Optional[str] = socket_path
        self._receiver: MessageReceiver
        self._sender: MessageSender
        self._receive_socket: Optional[Socket] = None
        self._send_socket: Optional[Socket] = None
        self._job_queue: JobQueue
        self._handlers: List = []
        self._chat_context: Dict[str, ChatContext] = {}
        self._exception_handler: Optional[Callable[[Exception, ChatContext],
                                                   Awaitable[None]]] = None
        self._raise_errors = raise_errors

        threading.current_thread().name = 'bot'
        logging.basicConfig(
            format='%(asctime)s %(threadName)s: [%(levelname)s] %(message)s',
            level=logging_level
        )
        self.log = logging.getLogger(__name__)

    def register_handler(self, regex: Union[str, Pattern], func: Callable) -> None:
        """Register a chat handler with a regex."""
        if not isinstance(regex, type(re.compile(""))):
            regex = re.compile(regex, re.UNICODE)

        self._handlers.append((regex, func))
        self.log.info(f"Handler <{func.__name__}> registered ('{regex.pattern}')")

    def set_exception_handler(self, func: Callable) -> None:
        self._exception_handler = func

    def handler(self, regex: Pattern) -> Callable:
        """Decorator to register handlers."""

        def decorator(func: Callable) -> Callable:
            self.register_handler(regex, func)
            return func

        return decorator

    async def _handle_message(self,
                              message: Message,
                              func: Callable, match: Match) -> None:
        """Handle a matched message."""
        message_id = id(message)

        # Get context id.
        group_id: Optional[str] = message.get_group_id()
        if group_id is not None:
            context_id = f"{group_id}+{message.source.uuid}"
        else:
            context_id = message.source.uuid

        # Retrieve or create chat context.
        if self._chat_context.get(context_id, False):
            context = self._chat_context[context_id]
            context.message = message
            context.match = match
            self.log.info(f"Chat context exists for {context_id}")
        else:
            context = ChatContext(message, match, self._job_queue, self)
            self.log.info(f"Chat context created for {context_id}")

            # Accept group invitation.
            if group_id is not None and self._group_auto_accept:
                await self.accept_invitation(group_id)

        # Process received message and send reply.
        try:
            await func(context)
            self._chat_context[context_id] = context
            self.log.debug(f"Message ({message_id}) processed by handler {func.__name__}")
        except StopPropagation:
            raise
        except Exception as exc:
            self.log.error(
                f"Processing message ({message_id}) by {func.__name__} failed",
                exc_info=exc,
            )
            if self._exception_handler:
                await self._exception_handler(exc, context)

    async def _match_message(self, message: Message) -> None:
        """Match an incoming message against a handler."""
        message_id = id(message)

        self.log.debug(f"Message ({message_id}) received from {message.source.uuid}")
        self.log.debug(str(message))

        # Loop over all registered handlers.
        for regex, func in self._handlers:
            # Match message text against handlers.
            match = re.search(regex, message.get_body())
            if not match:
                self.log.debug(f'skipping {func.__name__}')
                continue

            self.log.debug(
                f"Message matched against handler <{func.__name__}> ('{regex.pattern}')"
            )

            try:
                await self._handle_message(message, func, match)
            except StopPropagation:
                break

    async def __aenter__(self) -> 'Bot':
        """Connect to the bot's internal socket."""
        self._send_socket = await Socket(self._username,
                                         self._socket_path,
                                         False).__aenter__()
        self._sender = MessageSender(self._username, self._send_socket,
                                     self._raise_errors)
        return self

    async def __aexit__(self, *excinfo: Any) -> None:
        """Disconnect from the bot's internal socket."""
        if self._receive_socket:
            await self._receive_socket.__aexit__(*excinfo)
        if self._send_socket:
            await self._send_socket.__aexit__(*excinfo)

    async def start(self) -> None:
        """Start the bot event loop."""
        self.log.info("Bot started")
        self._receive_socket = await Socket(self._username,
                                            self._socket_path,
                                            True).__aenter__()
        self._receiver = MessageReceiver(self._receive_socket, self._sender)

        if self._profile_name:
            await self.set_profile(self._profile_name,
                                   self._profile_picture,
                                   self._profile_emoji,
                                   self._profile_about)

        async with anyio.create_task_group() as tg:
            self._job_queue = JobQueue(self._sender)
            await tg.spawn(self._job_queue.start)

            # handle incoming messages in parallel
            async for message in self._receiver.receive():
                if message.data_message is not None:
                    await tg.spawn(self._match_message, message)

    async def send_message(self, receiver: str, body: str,
                           attachments: Optional[List[Attachment]] = None,
                           link_previews: Optional[List[LinkPreview]] = None) -> bool:
        """
        Send a message.

        :param receiver:      The receiver of the message (uuid or number).
        :param body:          The body of the message.
        :param attachments:   Optional attachments to the message.
        :param link_previews: Optional link previews for the message.

        :return: Returns whether sending is successful
        :rtype: bool
        """
        return await self._sender.send_message(receiver, body, attachments, link_previews)

    async def set_profile(self,
                          profile_name: str,
                          profile_avatar: Optional[str] = None,
                          profile_emoji: Optional[str] = None,
                          profile_about: Optional[str] = None) -> None:
        """
        Set Signal profile.

        :param profile_name:   New profile name, empty string for no profile name.
        :param profile_avatar: Path to profile avatar file.
        :param profile_emoji:  Emoji character visible in profile.
        :param profile_about:  Description text visible in profile.
        """
        await self._sender.set_profile(profile_name,
                                       profile_avatar,
                                       profile_emoji,
                                       profile_about)

    async def set_expiration(self, receiver: str, time: int) -> None:
        """
        Set the message expiration timer for a chat.

        :param receiver: The receiver for which to set the expiration time.
        :param time:     Time must be specified in seconds, set to 0 to disable timer.
        """
        await self._sender.set_expiration(receiver, time)

    async def accept_invitation(self, group_id: str) -> None:
        """
        Accept a v2 group invitation.

        :param group_id: Group id to accept invitation from.
        """
        await self._sender.accept_invitation(group_id)

    async def list_groups(self) -> List[GroupV2]:
        """
        List of v2 groups for an account.

        :return: Returns a list of v2 group objects
        """
        return await self._sender.list_groups()

    async def get_group(self, group_id: str) -> GroupV2:
        """
        Get details of a group.

        :param group_id: Group id to get details for

        :return: Returns a GroupV2 object
        """
        return await self._sender.get_group(group_id)

    async def add_members(self, group_id: str, members: list) -> GroupV2:
        """
        Add members to a group.

        :param group_id: Group id to add the members to
        :param members:  List of members uuids to be added

        :return: Returns the updated GroupV2 object
        """
        return await self._sender.add_members(group_id, members)

    async def remove_members(self, group_id: str, members: list) -> GroupV2:
        """
        Remove members from a group.

        :param group_id: Group id to remove the members from
        :param members:  List of members uuids to be removed

        :return: Returns the updated GroupV2 object
        """
        return await self._sender.remove_members(group_id, members)

    async def create_group(self, title: str, members: list) -> GroupV2:
        """
        Create a Signal group.

        :param title: title for the new group
        :param members: List of members uuids to be added to the new group

        :return: Returns the created GroupV2 object
        """
        return await self._sender.create_group(title, members)

    async def leave_group(self, group_id: str) -> None:
        """
        Leave a Signal group.

        :param group_id: Identifier of the group to leave
        """
        await self._sender.leave_group(group_id)

    async def preview_group(self, url: str) -> GroupV2:
        """
        Preview information about a group without joining.

        :param url: Group invite link to preview information for

        :return: Returns a GroupV2 object
        """
        return await self._sender.preview_group(url)

    async def update_group_title(self, group_id: str, title: str) -> GroupV2:
        """
        Update a group’s title.

        :param group_id: Identifier of the group to update the title for
        :param title:    New title

        :return: Returns the updated GroupV2 object
        """
        return await self._sender.update_group_title(group_id, title)

    async def update_group_timer(self, group_id: str, timer: str) -> GroupV2:
        """
        Update a group’s timer.

        :param group_id: Identifier of the group to change timer of
        :param timer:    Expiration must be specified in seconds, 0 to disable timer

        :return: Returns the updated GroupV2 object
        """
        return await self._sender.update_group_timer(group_id, timer)

    async def update_group_role(self,
                                group_id: str,
                                member_id: str,
                                role: str) -> GroupV2:
        """
        Update role of a member in the group.

        :param group_id:  Identifier of the group to update member role for
        :param member_id: Identifier of the member
        :param role:      Updated role of the member

        :return: Returns the updated GroupV2 object
        """
        return await self._sender.update_group_role(group_id, member_id, role)

    async def update_group_avatar(self, group_id: str, avatar: str) -> GroupV2:
        """
        Change a group’s avatar

        :param group_id: id of the group to update avatar for.
        :param avatar: avatar path

        :return: Returns the updated group object
        """
        return await self._sender.update_group_avatar(group_id,  avatar)
