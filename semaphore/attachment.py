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
from __future__ import annotations
import attr
import logging
import re


@attr.s(auto_attribs=True)
class Attachment:
    """This object represents a Signal message attachment.
    The attributes have a 1 to 1 correspondance to the signald JsonAttachment class
    https://signald.org/protocol/structures/v1/JsonAttachment/
    """

    filename: str = attr.ib()
    blurhash: str = attr.ib(default=None)
    caption: str = attr.ib(default=None)
    content_type: str = attr.ib(default=None)
    custom_filename: str = attr.ib(default=None)
    digest: str = attr.ib(default=None)
    height: int = attr.ib(default=None)
    id: str = attr.ib(default=None)
    key: str = attr.ib(default=None)
    stored_filename:  str = attr.ib(default=None)
    size: int = attr.ib(default=None)
    voice_note: bool = attr.ib(default=None)
    width: int = attr.ib(default=None)

    @staticmethod
    def _snake_to_camel(attr_name: str) -> str:
        attr_name = re.sub(r"(_|-)+", " ", attr_name).title().replace(" ", "")
        return ''.join([attr_name[0].lower(), attr_name[1:]])

    def to_send_dict(self) -> dict:
        attachment_data = attr.asdict(self)
        send_data = {}
        for attr_name, value in attachment_data.items():
            if value is not None and attr_name != 'stored_filename':
                send_data[self._snake_to_camel(attr_name)] = value

        if self.filename is None:
            if self.stored_filename is None:
                raise ValueError("filename or stored_filename must be provided, found None")
            send_data["filename"] = self.stored_filename

        return send_data

    @staticmethod
    def create_from_receive_dict(data: dict) -> Attachment:
        log = logging.getLogger(__name__)

        attachment = Attachment(None)
        attachment_attr_names = attr.asdict(attachment)

        processed_data_attrs = set()
        for attr_name in attachment_attr_names:
            data_name = Attachment._snake_to_camel(attr_name)
            setattr(attachment, attr_name, data.get(data_name))
            processed_data_attrs.add(data_name)

        for attr_name in data:
            if attr_name not in processed_data_attrs:
                log.warning(f"Attribute {attr_name} in data was ignored")

        return attachment
