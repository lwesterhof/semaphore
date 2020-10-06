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


def alarm(ctx: ChatContext) -> None:
    ctx.message.reply("Beep! Beep! Beep!")


def set_timer(ctx: ChatContext) -> None:
    try:
        delta = int(ctx.match.group(1))
        alarm_time = time() + delta

        if 'job' in ctx.data:
            old_job = ctx.data["job"]
            old_job.schedule_removal()

        job = ctx.job_queue.run_once(alarm_time, alarm, ctx)
        ctx.data["job"] = job

        ctx.message.reply("Timer set!")
    except Exception:
        ctx.message.reply("'Usage: !timer <seconds>'")


def unset_timer(ctx: ChatContext) -> None:
    if 'job' in ctx.data:
        old_job = ctx.data["job"]
        old_job.schedule_removal()

    ctx.message.reply("Timer unset!")


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
