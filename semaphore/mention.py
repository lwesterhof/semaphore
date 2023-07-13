#!/usr/bin/env python
#
# Semaphore: A simple (rule-based) bot library for Signal Private Messenger.
# Copyright (C) 2023 Lazlo Westerhof <semaphore@lazlo.me>
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
"""This module contains an object that represents a Signal mention."""
import attr


@attr.s(auto_attribs=True, frozen=True)
class Mention:
    """This object represents a Signal mention.

    The attributes have a 1 to 1 correspondance to the signald JsonAddress class
    https://signald.org/protocol/structures/v1/JsonMention/
    """
    length: int
    start: int
    uuid: str

    @staticmethod
    def create_from_receive_dict(data: dict) -> 'Mention':
        return Mention(**data)
