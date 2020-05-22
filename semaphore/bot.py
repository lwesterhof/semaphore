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
import re
from datetime import datetime

from .message import Message
from .message_receiver import MessageReceiver
from .reply import Reply
from .socket import Socket


class Bot:
    """A simple (rule-based) Signal Private Messenger bot."""
    def __init__(self,
                 username,
                 debug=False,
                 socket_path="/var/run/signald/signald.sock"):
        self.username = username
        self.debug = debug
        self.socket = Socket(username, socket_path)
        self.handlers = []

    def __mark_read(self, message: Message):
        """
        Mark a Signal message you received as read.

        message: The Signal message you received.
        """
        self.socket.send({"type": "mark_read",
                          "username": self.username,
                          "recipientNumber": message.source,
                          "timestamps": [message.timestamp]})

    def __send_message(self, recipient: str, reply: Reply, recipient_group_id=None):
        """
        Send the bot message.

        recipient:          The recipient's phone number.
        reply:              The reply to send.
        recipient_group_id: Group id if recicpient is a group.
        """
        # Construct reply message.
        bot_message = {"type": "send",
                       "username": self.username,
                       "recipientNumber": recipient,
                       "messageBody": reply.message}

        # Add group id for group messages.
        if recipient_group_id:
            bot_message["recipientGroupId"] = recipient_group_id

        # Add attachments to message.
        if reply.attachments:
            bot_message["attachments"] = reply.attachments

        self.socket.send(bot_message)

    def log(self, message: str, timestamp=False):
        """
        Log messages, only when debug is enabled.

        message: Message to log.
        """
        if self.debug:
            if timestamp:
                now = datetime.now()
                timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
                print(f"{timestamp}: {message}")
            else:
                print(f"{message}")

    def register_handler(self, regex, func):
        """
        Register a chat handler with a regex.
        """
        if not isinstance(regex, type(re.compile(""))):
            regex = re.compile(regex, re.UNICODE)

        self.handlers.append((regex, func))

    def start(self):
        """
        Start the chat event loop.
        """
        receiver = MessageReceiver(self.socket)

        for message in receiver.receive():
            # Ignore empty messages.
            if message.empty():
                continue

            self.log("-" * 50)
            self.log("Message received", True)
            self.log(message)

            # Loop over all registered handlers.
            for regex, func in self.handlers:
                # Match message text against handlers.
                match = re.search(regex, message.get_text())
                if not match:
                    continue

                # Mark received message read before processing.
                try:
                    self.__mark_read(message)
                    self.log("Message marked as read", True)
                except Exception:
                    self.log("Marking message as read failed", True)

                # Process received message.
                try:
                    reply = func(message, match)
                    self.log(reply)
                except Exception:
                    self.log("Reply failed", True)
                    continue

                # Send bot message.
                try:
                    self.__send_message(recipient=message.source,
                                        reply=reply,
                                        recipient_group_id=message.get_group_id())
                    self.log("Reply send", True)
                except Exception:
                    self.log("Sending reply failed", True)
                    continue

                # Stop matching.
                if reply.stop:
                    break
