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
"""This module contains an object that represents a Signal Private Messenger bot."""
import logging
import re
import threading
from datetime import datetime
from typing import Dict

from .chat_context import ChatContext
from .job_queue import JobQueue
from .message import Message
from .message_receiver import MessageReceiver
from .message_sender import MessageSender
from .socket import Socket


class Bot:
    """This object represents a simple (rule-based) Signal Private Messenger bot."""

    def __init__(self,
                 username,
                 logging_level=logging.INFO,
                 socket_path="/var/run/signald/signald.sock"):
        """Initialize bot."""
        self._username: str = username
        self._receiver = None
        self._sender = None
        self._job_queue = None
        self._handlers = []
        self._chat_context: Dict[str, ChatContext] = {}

        threading.current_thread().name = 'bot'
        logging.basicConfig(
            format='%(asctime)s %(threadName)s: [%(levelname)s] %(message)s',
            level=logging_level
        )
        self.log = logging.getLogger(__name__)
        self.log.info("Bot initialized")

        self._socket = Socket(username, socket_path)

    def register_handler(self, regex, func, job=False) -> None:
        """Register a chat handler with a regex."""
        if not isinstance(regex, type(re.compile(""))):
            regex = re.compile(regex, re.UNICODE)

        self._handlers.append((regex, func, job))
        self.log.info(f"Handler registered ('{regex.pattern}')")

    def handle_message(self, message: Message) -> None:
        """Handle an incoming message."""
        message_id = id(message)
        message_source = message.get_redacted_source()
        self.log.info(f"Message ({message_id}) received from {message_source}")
        self.log.debug(str(message))

        # Loop over all registered handlers.
        for regex, func, job in self._handlers:
            # Match message text against handlers.
            match = re.search(regex, message.get_body())
            if not match:
                continue

            # Retrieve or create chat context.
            if self._chat_context.get(message.source, False):
                context = self._chat_context[message.source]
                context.message = message
                context.match = match
                self.log.info(f"Chat context exists for {message_source}")
            else:
                context = ChatContext(message, match, self._job_queue)
                self.log.info(f"No chat context found for {message_source}")
                self.log.info(f"Chat context created for {message_source}")

            # Process received message and send reply.
            try:
                self._sender.mark_read(message)
                self.log.info(f"Message ({message_id}) marked as read")

                reply = func(context)
                self._chat_context[message.source] = context
                self.log.info(f"Message ({message_id}) processed by handler")

                self._sender.send_message(message, reply)
                self.log.info(f"Reply for message ({message_id}) "
                              f"sent to {message_source}")
                self.log.debug(reply)
            except Exception:
                self.log.warning(f"Processing message ({message_id}) failed")
                continue

            # Stop matching.
            if reply.stop:
                break

    def start(self) -> None:
        """Start the bot event loop."""
        self.log.info("Bot started")

        # Initialize sender and receiver.
        self._receiver = MessageReceiver(self._socket)
        self._sender = MessageSender(self._username, self._socket)

        # Initialize job queue.
        self._job_queue = JobQueue(self._sender)
        job_queue = threading.Thread(name='job_queue',
                                     target=self._job_queue.start)
        job_queue.start()

        for message in self._receiver.receive():
            # Only handle non empty messages.
            if not message.empty():
                self.handle_message(message)
