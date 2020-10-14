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
from typing import List, Optional, TYPE_CHECKING

import attr

if TYPE_CHECKING:
    from .sticker import Sticker


@attr.s(auto_attribs=True, frozen=True)
class StickerPack:
    """This object represents a Signal sticker pack."""

    pack_id: str
    pack_key: str
    stickers: List['Sticker'] = attr.ib(factory=list)
    # inbound partial sticker packs do not have title and author set
    title: Optional[str] = None
    author: Optional[str] = None

    @property
    def url(self) -> str:
        """Return the pack's URL."""
        return f'https://signal.art/addstickers/#pack_id={self.pack_id}&pack_key={self.pack_key}'  # noqa: E501
