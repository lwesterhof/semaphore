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
import contextlib
import io
import os
import re
from heapq import heappop, heappush
from time import time

from semaphore import Bot, ChatContext, StopPropagation


async def alarm(ctx: ChatContext) -> None:
    with contextlib.suppress(IndexError):
        del ctx.data['jobs'][0]
    await ctx.message.reply("Beep! Beep! Beep!")


async def set_timer(ctx: ChatContext) -> None:
    try:
        delta = int(ctx.match.group(1))
    except ValueError:
        await ctx.message.reply("Usage: !timer <seconds>")
        return

    alarm_time = time() + delta

    job = await ctx.job_queue.run_once(alarm_time, alarm, ctx)
    heap = ctx.data.setdefault("jobs", [])
    heappush(heap, (alarm_time, job))

    await ctx.message.reply("Timer set!")


async def list_timers(ctx: ChatContext) -> None:
    jobs = ctx.data.setdefault("jobs", [])
    if not jobs:
        await ctx.message.reply("No timers scheduled.")
        raise StopPropagation

    menu = io.StringIO()
    now = time()
    for job_id, (timestamp, job) in enumerate(jobs, 1):
        menu.write(f"{job_id}: In {timestamp - now:.0f} seconds\n")

    menu.write("\nUse !timer unset <id> to unset a specific timer.")

    await ctx.message.reply(menu.getvalue())

    raise StopPropagation


async def unset_timer(ctx: ChatContext) -> None:
    jobs = ctx.data.setdefault("jobs", [])

    try:
        job_id = int(ctx.match.group(1)) - 1
        if job_id not in range(len(jobs)):
            raise ValueError
    except ValueError:
        await ctx.message.reply(
            "Usage: !timer unset <timer id>. "
            "Get a list of them using !timer list."
        )
        raise StopPropagation

    del jobs[job_id]
    await ctx.message.reply("Timer unset!")

    raise StopPropagation


async def main():
    """Start the bot."""
    # Connect the bot to number.
    async with Bot(os.environ["SIGNAL_PHONE_NUMBER"]) as bot:
        bot.register_handler(re.compile("!timer unset (.*)"), unset_timer)
        bot.register_handler(re.compile("!timer list"), list_timers)
        bot.register_handler(re.compile("!timer (.*)"), set_timer)

        # Run the bot until you press Ctrl-C.
        await bot.start()


if __name__ == '__main__':
    import anyio
    anyio.run(main)
