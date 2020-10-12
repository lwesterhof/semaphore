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
"""This module contains an object that represents a bot job."""

from datetime import datetime
from typing import Optional

from dateutil.relativedelta import relativedelta

from .message import Message
from .reply import Reply


class Job(object):
    """This object represents a bot job."""

    def __init__(self, handler, context, repeat=False, monthly=False, interval=None):
        """Initialize job."""
        self._handler = handler
        self._context = context
        self._repeat: bool = repeat
        self._interval: int = interval
        self._monthly: bool = monthly
        self._remove: bool = False

    def get_message(self) -> Message:
        """Get the message of this job."""
        return self._context.message

    def get_interval(self) -> float:
        """Get the interval of the (repeating) job."""
        if self._repeat:
            if self._monthly:
                now = datetime.now()
                next_month = now + relativedelta(months=+1)
                interval = next_month.timestamp() - now.timestamp()
                return interval
            else:
                return self._interval
        else:
            return 0.0

    def is_repeating(self) -> bool:
        """Check if the job is repeating."""
        return self._repeat

    def schedule_removal(self) -> None:
        """Schedule the job for removal from the job queue."""
        self._remove = True

    def remove(self) -> bool:
        """Check if job should be removed."""
        return self._remove

    async def run(self) -> Optional[Reply]:
        """Run the job by calling the handler."""
        return await self._handler(self._context)
