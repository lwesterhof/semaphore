#!/usr/bin/env python
#
# Semaphore: A simple (rule-based) bot library for Signal Private Messenger.
# Copyright (C) 2020
# Lazlo Westerhof <semaphore@lazlo.me>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
from datetime import datetime
from typing import Optional

from dateutil.relativedelta import relativedelta

from .message import Message
from .reply import Reply


class Job(object):
    def __init__(self, handler, context, repeat=False, monthly=False, interval=None):
        self._handler = handler
        self._context = context
        self._repeat: bool = repeat
        self._interval: int = interval
        self._monthly: bool = monthly
        self._remove: bool = False

    def get_message(self) -> Message:
        return self._context.message

    def get_interval(self) -> float:
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
        return self._repeat

    def schedule_removal(self) -> None:
        self._remove = True

    def remove(self) -> bool:
        return self._remove

    def run(self) -> Optional[Reply]:
        # Process received message.
        try:
            reply = self._handler(self._context)
            return reply
        except Exception:
            return None
