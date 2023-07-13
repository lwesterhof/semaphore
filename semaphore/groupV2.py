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
"""This module contains an object that represents Signal group v2 info."""
import logging
import re
from typing import Dict, List

import attr

from .address import Address


@attr.s(auto_attribs=True)
class GroupV2:
    """This object represents Signal group v2 info.

    The attributes have a 1 to 1 correspondance to the signald JsonGroupV2Info class
    https://signald.org/protocol/structures/v1/JsonGroupV2Info/
    """
    id: str
    announcements: str = attr.ib(default=None)
    avatar: str = attr.ib(default=None)
    description: str = attr.ib(default=None)
    inviteLink: str = attr.ib(default=None)
    removed: bool = attr.ib(default=None)
    revision: int = attr.ib(default=None)
    timer: int = attr.ib(default=None)
    title: str = attr.ib(default=None)
    member_detail: List[dict] = attr.ib(default=[])
    members: List[Address] = attr.ib(default=[])
    pending_members: List[Address] = attr.ib(default=[])
    requesting_members: List[Address] = attr.ib(default=[])

    @staticmethod
    def _snake_to_camel(attr_name: str) -> str:
        attr_name = re.sub(r"(_|-)+", " ", attr_name).title().replace(" ", "")
        return ''.join([attr_name[0].lower(), attr_name[1:]])

    @staticmethod
    def create_from_receive_dict(data: dict) -> 'GroupV2':
        log = logging.getLogger(__name__)

        group = GroupV2("")
        group_attr_names = attr.asdict(group)

        processed_data_attrs = set()
        for attr_name in group_attr_names:
            data_name = GroupV2._snake_to_camel(attr_name)
            setattr(group, attr_name, data.get(data_name))
            processed_data_attrs.add(data_name)

        for attr_name in data:
            if attr_name not in processed_data_attrs:
                log.warning(f"Attribute {attr_name} in data was ignored")

        return group
