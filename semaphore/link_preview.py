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
"""This module contains an object that represents a Signal message link preview."""
import logging
import re
from typing import Optional

import attr

from .attachment import Attachment


@attr.s(auto_attribs=True)
class LinkPreview:
    """This object represents a Signal message link preview.

    The attributes have a 1 to 1 correspondance to the signald JsonPreview class
    https://signald.org/protocol/structures/v1/JsonPreview/
    """
    attachment: Attachment = attr.ib(default=None)
    date: int = attr.ib(default=None)
    description: str = attr.ib(default=None)
    title: str = attr.ib(default=None)
    url: str = attr.ib(default=None)

    def to_send_dict(self) -> dict:
        send_data = attr.asdict(self)
        if self.attachment is not None:
            send_data['attachment'] = self.attachment.to_send_dict()

        return send_data

    @staticmethod
    def create_from_receive_dict(data: dict) -> 'LinkPreview':
        processed_data = data.copy()
        if 'attachment' in processed_data:
            attachment = Attachment.create_from_receive_dict(data['attachment'])
            processed_data['attachment'] = attachment

        return LinkPreview(**processed_data)
