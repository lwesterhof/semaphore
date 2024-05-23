
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
"""This module contains an object that represents a Signal data message."""
from __future__ import annotations

from typing import List, TYPE_CHECKING, Optional

import attr

if TYPE_CHECKING:
    from .attachment import Attachment
    from .mention import Mention

@attr.s(auto_attribs=True, frozen=True)
class QuotedAttachment:
    """This object represents an attachment in a quoted Signal message."""
    content_type: str = attr.ib(default=None)
    filename: str = attr.ib()
    thumbnail: Optional[Attachment] = attr.ib(default=None)

    @staticmethod
    def create_from_receive_dict(data: dict) -> QuotedAttachment:
        """Create a QuotedAttachment from a receive dict."""
        return QuotedAttachment(
            content_type=data["contentType"],
            filename=data["fileName"],
            thumbnail=Attachment.create_from_receive_dict(data["thumbnail"])
            if data["thumbnail"]
            else None,
        )

@attr.s(auto_attribs=True, frozen=True)
class QuotedMessage:
    """This object represents a quoted Signal message."""

    timestamp: int
    body: str
    attachments: List[QuotedAttachment] = attr.ib(factory=list)
    mentions: List[Mention] = attr.ib(factory=list)

    @staticmethod
    def create_from_receive_dict(data: dict) -> QuotedMessage:
        """Create a QuotedMessage from a receive dict."""
        return QuotedMessage(
            timestamp=data["id"],
            body=data["text"],
            attachments=[
                QuotedAttachment.create_from_receive_dict(attachment)
                for attachment in data["attachments"]
            ],
            mentions=[
                Mention.create_from_receive_dict(mention)
                for mention in data["mentions"]
            ],
        )