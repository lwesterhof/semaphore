#!/usr/bin/env python
#
# Semaphore: A simple (rule-based) bot library for Signal Private Messenger.
# Copyright (C) 2021 Lazlo Westerhof <semaphore@lazlo.me>
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
"""
Signal Bot example, broadcast to all subscribers.
"""
import os
from time import time
from typing import Dict

from semaphore import Bot, ChatContext

subscribers: Dict[str, float] = {}


async def subscribe(ctx: ChatContext) -> None:
    try:
        if ctx.message.source.uuid in subscribers:
            await ctx.message.reply("Already subscribed!")
        else:
            subscribers[ctx.message.source.uuid] = time()
            await ctx.message.reply("Subscription successful!")
    except Exception:
        await ctx.message.reply("Could not subscribe!")


async def unsubscribe(ctx: ChatContext) -> None:
    try:
        if ctx.message.source.uuid in subscribers:
            del subscribers[ctx.message.source.uuid]
            await ctx.message.reply("Successfully unsubscribed!")
        else:
            await ctx.message.reply("Not subscribed!")
    except Exception:
        await ctx.message.reply("Could not unsubscribe!")


async def broadcast(ctx: ChatContext) -> None:
    await ctx.message.mark_read()
    message = ctx.message.get_body()[len("!broadcast"):].strip()

    # Broadcast message to all subscribers.
    for subscriber in subscribers:
        if await ctx.bot.send_message(subscriber, message):
            print(f"Message successfully sent to {subscriber}")
        else:
            print(f"Could not send message to {subscriber}")
            del subscribers[subscriber]


async def main():
    """Start the bot."""
    # Connect the bot to number.
    async with Bot(os.environ["SIGNAL_PHONE_NUMBER"]) as bot:
        bot.register_handler("!subscribe", subscribe)
        bot.register_handler("!unsubscribe", unsubscribe)
        bot.register_handler("!broadcast", broadcast)

        # Run the bot until you press Ctrl-C.
        await bot.start()


if __name__ == '__main__':
    import anyio
    anyio.run(main)
