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
"""This module contains an object that represents a Signal sticker."""
from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

import attr

if TYPE_CHECKING:
    from .sticker_pack import StickerPack


@attr.s(auto_attribs=True, frozen=True)
class Sticker:
    """This object represents a Signal sticker."""

    pack: StickerPack
    sticker_id: int
    # inbound Signal messages don't specify the emoji of a sticker
    emoji: Optional[str] = None
