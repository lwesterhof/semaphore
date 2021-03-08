#!/usr/bin/env python
#
# Semaphore: A simple (rule-based) bot library for Signal Private Messenger.
# Copyright (C) 2020-2021 Lazlo Westerhof <semaphore@lazlo.me>
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
"""This module contains an object that represents a bot job queue."""
import logging
from time import time
from typing import Callable

from anyio import sleep, WouldBlock

from .exceptions import StopPropagation
from .job import Job
from .queue import PriorityQueue


class JobQueue:
    """"This object represents a bot job queue."""

    def __init__(self, sender):
        """Initialize job queue."""
        self._queue = PriorityQueue()
        self._sender = sender

        self.log = logging.getLogger(__name__)

    async def run_once(
        self,
        timestamp: float,
        callback: Callable,
        context,
    ) -> Job:
        """Add a job to the queue that runs once."""
        job = Job(callback, context)
        await self._queue.put_nowait(timestamp, job)
        self.log.info(f"Put job ({id(job)}) in the queue")
        return job

    async def run_repeating(self,
                            timestamp: float,
                            callback: Callable,
                            context,
                            interval: int) -> Job:
        """Add a job to the queue that runs repeating."""
        job = Job(callback, context, repeat=True, interval=interval)
        await self._queue.put_nowait(timestamp, job)
        self.log.info(f"Put repeating job ({id(job)}) in the queue")
        return job

    async def run_daily(self,
                        timestamp: float,
                        callback: Callable,
                        context) -> Job:
        """Add a job to the queue that runs daily."""
        interval = 60 * 60 * 24  # Day
        job = Job(callback, context, repeat=True, interval=interval)
        await self._queue.put_nowait(timestamp, job)
        self.log.info(f"Put daily job ({id(job)}) in the queue")
        return job

    async def run_monthly(self,
                          timestamp: float,
                          callback: Callable,
                          context) -> Job:
        """Add a job to the queue that runs monthly."""
        job = Job(callback, context, repeat=True, monthly=True)
        await self._queue.put_nowait(timestamp, job)
        self.log.info(f"Put monthly job ({id(job)}) in the queue")
        return job

    async def start(self) -> None:
        """Run all the jobs in the queue that are due."""
        self.log.info("Job queue started")

        while True:
            now = time()

            try:
                timestamp, job = self._queue.get_nowait()
            except WouldBlock:
                await sleep(1)
                continue

            if timestamp > now:
                await self._queue.put_nowait(timestamp, job)
                await sleep(1)
                continue

            if job.remove():
                self.log.info(f"Removed job ({id(job)}) from queue")
                continue

            self.log.info(f"Running job ({id(job)})")
            message = job.get_message()
            try:
                reply = await job.run()
                if reply:
                    await self._sender.reply_message(message, reply)
                    self.log.info(f"Reply for job ({id(job)}) "
                                  f"sent to {message.source.uuid}")
            except StopPropagation:
                continue
            except Exception as exc:
                self.log.warning(f"Sending reply for message ({id(message)}) "
                                 f"to {message.source.uuid} failed",
                                 exc_info=exc)
                continue

            if job.is_repeating():
                interval = job.get_interval()
                await self._queue.put_nowait(now + interval, job)
                self.log.info(f"Added repeating job ({id(job)}) to the queue")
