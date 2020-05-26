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
import logging
import re
from datetime import datetime
from threading import Thread
from typing import Dict

from .chat_context import ChatContext
from .job_queue import JobQueue
from .message_receiver import MessageReceiver
from .message_sender import MessageSender
from .socket import Socket


class Bot:
    """A simple (rule-based) Signal Private Messenger bot."""
    def __init__(self,
                 username,
                 logging_level=logging.INFO,
                 socket_path="/var/run/signald/signald.sock"):
        self._username: str = username
        self._socket = Socket(username, socket_path)
        self._receiver = None
        self._sender = None
        self._job_queue = None
        self._handlers = []
        self._chat_context: Dict[str, ChatContext] = {}

        logging.basicConfig(
            format='%(asctime)s %(threadName)s: [%(levelname)s] %(message)s',
            level=logging_level
        )
        self.log = logging.getLogger(__name__)

    def register_handler(self, regex, func, job=False) -> None:
        """
        Register a chat handler with a regex.
        """
        if not isinstance(regex, type(re.compile(""))):
            regex = re.compile(regex, re.UNICODE)

        self._handlers.append((regex, func, job))
        self.log.info(f"Handler registered ('{regex.pattern}')")

    def start(self) -> None:
        """
        Start the bot event loop.
        """
        self.log.info("Bot started")

        # Initialize sender and receiver.
        self._receiver = MessageReceiver(self._socket)
        self._sender = MessageSender(self._username, self._socket)

        # Initialize job queue.
        self._job_queue = JobQueue(self._sender)
        job_queue = Thread(name='job_queue',
                           target=self._job_queue.start)
        job_queue.start()

        for message in self._receiver.receive():
            # Ignore empty messages.
            if message.empty():
                continue

            self.log.info("Message received")
            self.log.debug(str(message))

            # Loop over all registered handlers.
            for regex, func, job in self._handlers:
                # Match message text against handlers.
                match = re.search(regex, message.get_text())
                if not match:
                    continue

                # Retrieve or create chat context.
                if self._chat_context.get(message.source, False):
                    context = self._chat_context[message.source]
                    context.message = message
                    context.match = match
                    self.log.info("Chat context exists")
                else:
                    context = ChatContext(message, match, self._job_queue)
                    self.log.info("No chat context found, created one")

                # Mark received message read before processing.
                self._sender.mark_read(message)
                try:
                    self._sender.mark_read(message)
                    self.log.info("Message marked as read")
                except Exception:
                    self.log.warning("Marking message as read failed")

                # Process received message.
                try:
                    reply = func(context)
                    self.log.info("Message processed by handler")
                    self.log.debug(reply)
                    self._chat_context[message.source] = context
                except Exception:
                    self.log.warning("Reply failed")
                    continue

                # Send bot message.
                try:
                    self._sender.send_message(message, reply)
                    self.log.info("Reply send")
                except Exception:
                    self.log.warning("Sending reply failed")
                    continue

                # Stop matching.
                if reply.stop:
                    break
