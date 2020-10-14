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
"""This module contains an object that represents a Signal Private Messenger bot."""
import logging
import re
import threading
from datetime import datetime
from typing import Any, Callable, Dict, List, Pattern, TYPE_CHECKING

import anyio

from .chat_context import ChatContext
from .job_queue import JobQueue
from .message import Message
from .message_receiver import MessageReceiver
from .message_sender import MessageSender
from .socket import Socket


class StopPropagation(Exception):
    """Raise this to prevent further handlers from running on this message."""


class Bot:
    """This object represents a simple (rule-based) Signal Private Messenger bot."""

    def __init__(self,
                 username: str,
                 logging_level=logging.INFO,
                 socket_path="/var/run/signald/signald.sock"):
        """Initialize bot."""
        self._username: str = username
        self._socket_path: str = socket_path
        self._receiver: MessageReceiver
        self._sender: MessageSender
        self._job_queue: JobQueue
        self._handlers: List = []
        self._chat_context: Dict[str, ChatContext] = {}

        threading.current_thread().name = 'bot'
        logging.basicConfig(
            format='%(asctime)s %(threadName)s: [%(levelname)s] %(message)s',
            level=logging_level
        )
        self.log = logging.getLogger(__name__)

        self._socket: Socket

    def register_handler(self, regex: Pattern, func: Callable) -> None:
        """Register a chat handler with a regex."""
        if not isinstance(regex, type(re.compile(""))):
            regex = re.compile(regex, re.UNICODE)

        self._handlers.append((regex, func))
        self.log.info(f"Handler <{func.__name__}> registered ('{regex.pattern}')")

    def handler(self, regex: Pattern):
        """Decorator to register handlers."""
        def decorator(func: Callable):
            self.register_handler(regex, func)
            return func
        return decorator

    async def _handle_message(self, message: Message, func: Callable, match) -> None:
        """Handle a matched message."""
        message_id = id(message)
        message_source = message.get_redacted_source()

        # Retrieve or create chat context.
        if self._chat_context.get(message.source, False):
            context = self._chat_context[message.source]
            context.message = message
            context.match = match
            self.log.debug(f"Chat context exists for {message_source}")
        else:
            context = ChatContext(message, match, self._job_queue, self)
            self.log.debug(f"Chat context created for {message_source}")

        # Process received message and send reply.
        try:
            await func(context)
            self._chat_context[message.source] = context
            self.log.debug(f"Message ({message_id}) processed by handler {func.__name__}")
        except StopPropagation:
            raise
        except Exception as exc:
            self.log.error(
                f"Processing message ({message_id}) by {func.__name__} failed",
                exc_info=exc,
            )

    async def _match_message(self, message: Message) -> None:
        """Match an incoming message against a handler."""
        message_id = id(message)
        message_source = message.get_redacted_source()

        # Mark message as delivered.
        await message.mark_delivered()
        self.log.debug(f"Message ({message_id}) received from {message_source}")
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
        self._socket = await Socket(self._username, self._socket_path).__aenter__()
        return self

    async def __aexit__(self, *excinfo):
        """Disconnect from the bot's internal socket."""
        return await self._socket.__aexit__(*excinfo)

    async def start(self) -> None:
        """Start the bot event loop."""
        self.log.info("Bot started")

        self._sender = MessageSender(self._username, self._socket)
        self._receiver = MessageReceiver(self._socket, self._sender)

        async with anyio.create_task_group() as tg:
            self._job_queue = JobQueue(self._sender)
            await tg.spawn(self._job_queue.start)

            # handle incoming messages in parallel
            async for message in self._receiver.receive():
                if message.data_message is not None:
                    await tg.spawn(self._match_message, message)
