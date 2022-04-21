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
"""This module contains an object that represents a Signal data message."""
from typing import List, Optional

import attr

from .attachment import Attachment
from .group import Group
from .groupV2 import GroupV2
from .link_preview import LinkPreview
from .sticker import Sticker


@attr.s(auto_attribs=True, frozen=True)
class DataMessage:
    """This object represents a Signal data message."""

    timestamp: int
    body: str
    expires_in_seconds: int = attr.ib(default=0)
    attachments: List[Attachment] = attr.ib(factory=list)
    group: Optional[Group] = attr.ib(default=None)
    groupV2: Optional[GroupV2] = attr.ib(default=None)
    sticker: Optional[Sticker] = attr.ib(default=None)
    previews: List[LinkPreview] = attr.ib(factory=list)
