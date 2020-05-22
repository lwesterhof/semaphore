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
import attr

from .attachment import Attachment
from .group_info import GroupInfo


@attr.s(auto_attribs=True, frozen=True)
class DataMessage:
    """This object represents a Signal data message."""
    timestamp: int
    message: str
    expires_in_seconds: int = attr.ib(default=0)
    attachments: [Attachment] = attr.ib(default=[])
    group_info: GroupInfo = attr.ib(default=None)
