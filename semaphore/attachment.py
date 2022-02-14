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
"""This module contains an object that represents a Signal message attachment."""
import attr
import re

@attr.s(auto_attribs=True, frozen=True)
class Attachment:
    """This object represents a Signal message attachment."""

    content_type: str
    id: str
    size: int
    stored_filename: str
    custom_filename: str = attr.ib(default=None)
    width: int = attr.ib(default=0)
    height: int = attr.ib(default=0)

    @staticmethod
    def _snake_to_camel(attr_name: str):
        attr_name = re.sub(r"(_|-)+", " ", attr_name).title().replace(" ", "")
        return ''.join([attr_name[0].lower(), attr_name[1:]])

    def to_send_dict(self):
        snake_dict_attachment = attr.asdict(self)
        camel_dict_attachment = {}
        for key, value in snake_dict_attachment.items():
            camel_dict_attachment[self._snake_to_camel(key)] = value

        camel_dict_attachment["filename"] = self.stored_filename

        return camel_dict_attachment
