#!/usr/bin/env python
#
# Semaphore: A simple (rule-based) bot library for Signal Private Messenger.
# Copyright (C) 2020-2022 Lazlo Westerhof <semaphore@lazlo.me>
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
"""This module contains an object that represents a bot reply."""
from typing import List

import attr

from .attachment import Attachment
from .link_preview import LinkPreview


@attr.s(auto_attribs=True, frozen=True)
class Reply:
    """This object represents a Bot reply."""

    body: str
    attachments: List[Attachment] = attr.ib(default=[])
    quote: bool = attr.ib(default=False)
    reaction: bool = attr.ib(default=False)
    mark_read: bool = attr.ib(default=True)
    link_previews: List[LinkPreview] = attr.ib(default=[])
