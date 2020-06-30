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
"""This module contains an object that represents a Signal message."""
from typing import Optional

import attr

from .data_message import DataMessage


@attr.s(auto_attribs=True, frozen=True)
class Message:
    """This object represents a Signal message."""

    username: str
    source: str
    envelope_type: int
    timestamp: int
    timestamp_iso: str
    server_timestamp: int
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

    def get_redacted_source(self) -> str:
        """Return the message source redacted."""
        return f"+********{self.source[-3:]}"

    def get_body(self):
        """Check if the message is not empty."""
        if self.empty():
            return ""
        else:
            return self.data_message.body

    def get_group_id(self) -> Optional[str]:
        """Get group id if message is a group message."""
        if self.data_message and self.data_message.group_info:
            return self.data_message.group_info.group_id
        else:
            return None
