#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0

"""PriorityQueue implementation for anyio."""
from heapq import heappop, heappush
from typing import List, Tuple

import anyio
from anyio import WouldBlock

from .job import Job


class PriorityQueue:
    """PriorityQueue implementation for anyio."""

    def __init__(self) -> None:
        """Initialize PriorityQueue."""
        self._not_empty = anyio.create_event()
        self._queue: List = []
        self._counter = 0

    async def put_nowait(self, prio: float, item: Job) -> None:
        """Put an item into the queue without blocking."""
        heappush(self._queue, (prio, self._counter, item))
        self._counter += 1
        if not self._not_empty.is_set():
            await self._not_empty.set()

    def get_nowait(self) -> Tuple[float, Job]:
        """Remove and return an item if one is immediately available.

        :raises WouldBlock: If no item is immediately available

        :returns: Item from the queue
        """
        if not self._not_empty.is_set():
            raise WouldBlock

        prio, _, item = heappop(self._queue)

        if not self._queue:
            self._not_empty = anyio.create_event()

        return prio, item
