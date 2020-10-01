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
"""
Signal Bot example, sends an alert after a specified time.
"""
import re
from time import time

from semaphore import Bot, ChatContext


def alarm(context: ChatContext) -> None:
    context.message.reply(body="Beep! Beep! Beep!")


def set_timer(context: ChatContext) -> None:
    try:
        delta = int(context.match.group(1))
        alarm_time = time() + delta

        if 'job' in context.data:
            old_job = context.data["job"]
            old_job.schedule_removal()

        job = context.job_queue.run_once(alarm_time, alarm, context)
        context.data["job"] = job

        context.message.mark_read()
        context.message.reply(body="Timer set!")
    except Exception:
        context.message.mark_read()
        context.message.reply(body="'Usage: !timer <seconds>'")


def unset_timer(context: ChatContext) -> None:
    if 'job' in context.data:
        old_job = context.data["job"]
        old_job.schedule_removal()

    context.message.mark_read()
    context.message.reply(body="Timer unset!")


def main():
    """Start the bot."""
    # Connect the bot to number.
    bot = Bot("+xxxxxxxxxxx")

    # Add timer handler.
    bot.register_handler(re.compile("!timer unset"), unset_timer)
    bot.register_handler(re.compile("!timer (.*)"), set_timer)

    # Run the bot until you press Ctrl-C.
    bot.start()


if __name__ == '__main__':
    main()
