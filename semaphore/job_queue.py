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
from threading import Thread
from queue import Empty, PriorityQueue
from time import sleep, time
from typing import Callable

from .job import Job


class JobQueue:
    def __init__(self, sender):
        self._queue = PriorityQueue()
        self._sender = sender

    def run_once(self,
                 timestamp: float,
                 callback: Callable,
                 context) -> Job:
        job = Job(callback, context)
        self._queue.put((timestamp, job))
        return job

    def run_repeating(self,
                      timestamp: float,
                      callback: Callable,
                      context,
                      interval: int) -> Job:
        job = Job(callback, context, repeat=True, interval=interval)
        self._queue.put((timestamp, job))
        return job

    def run_daily(self,
                  timestamp: float,
                  callback: Callable,
                  context) -> Job:
        interval = 60 * 60 * 24  # Day
        job = Job(callback, context, repeat=True, interval=interval)
        self._queue.put((timestamp, job))
        return job

    def run_monthly(self,
                    timestamp: float,
                    callback: Callable,
                    context) -> Job:
        job = Job(callback, context, repeat=True, monthly=True)
        self._queue.put((timestamp, job))
        return job

    def start(self) -> None:
        """Run all the jobs in the queue that are due."""

        while True:
            now = time()

            try:
                timestamp, job = self._queue.get(False)
            except Empty:
                sleep(1)
                continue

            if timestamp > now:
                self._queue.put((timestamp, job))
                sleep(1)
                continue

            if job.remove():
                continue

            try:
                reply = job.run()
                if reply:
                    self._sender.send_message(job.get_message(), reply)
            except Exception:
                continue

            if job.is_repeating():
                interval = job.get_interval()
                self._queue.put((now + interval, job))
