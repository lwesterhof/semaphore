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
from queue import Empty, PriorityQueue
from time import sleep, time

from .job import Job


class JobQueue:
    def __init__(self, sender):
        self._queue = PriorityQueue()
        self._sender = sender

    def put(self, timestamp, callback, message):
        job = Job(callback, message)
        self._queue.put((timestamp, job))

    def start(self):
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

            reply = job.run()
            self._sender.send_message(job.get_message(), reply)
