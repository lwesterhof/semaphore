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
"""This module contains an object that represents a Signal profile."""
import logging
from typing import Dict, List

import attr

from .address import Address


@attr.s(auto_attribs=True)
class Profile:
    """This object represents a Signal profile.

    The attributes have a 1 to 1 correspondance to the signald Profile class
    https://signald.org/protocol/structures/v1/Profile/
    """
    about: str = attr.ib(default=None)
    address: Address = attr.ib(default=None)
    avatar: str = attr.ib(default=None)
    capabilities: Dict[str, bool] = attr.ib(default={})
    color: str = attr.ib(default=None)
    contact_name: str = attr.ib(default=None)
    emoji: str = attr.ib(default=None)
    expiration_time: int = attr.ib(default=None)
    inbox_position: int = attr.ib(default=None)
    mobilecoin_address: str = attr.ib(default=None)
    name: str = attr.ib(default=None)
    profile_name: str = attr.ib(default=None)
    visible_badge_ids: List[str] = attr.ib(default=None)

    @staticmethod
    def create_from_receive_dict(data: dict) -> 'Profile':
        log = logging.getLogger(__name__)

        profile = Profile("")
        profile_attr_names = attr.asdict(profile)

        processed_data_attrs = set()
        for attr_name in profile_attr_names:
            if attr_name == 'address' and data.get('address'):
                address = Address.create_from_receive_dict(data['address'])
                setattr(profile, attr_name, address)
            else:
                setattr(profile, attr_name, data.get(attr_name))

            processed_data_attrs.add(attr_name)

        for attr_name in data:
            if attr_name not in processed_data_attrs:
                log.warning(f"Attribute {attr_name} in data was ignored")

        return profile
