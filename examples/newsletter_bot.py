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
"""
Signal Bot example, repeats received messages.
"""
import os
from typing import List

from semaphore import Bot, ChatContext


class NewsletterBot:
    bot: Bot
    subscribers: List[str] = []

    def __init__(self, bot: Bot):
        self.bot = bot

        bot.register_handler("!subscribe", self.subscribeHandler)
        bot.register_handler("!sendToAll", self.sendHandler)

    async def subscribeHandler(self, ctx: ChatContext) -> None:
        self.subscribers.append(ctx.message.source)
        await ctx.message.reply("Subscription successful!")

    async def sendHandler(self, ctx: ChatContext) -> None:
        message = ctx.message.get_body()[len("!sendToAll"):].strip()

        # Send message to all subscribers without using ChatContext
        for subscriber in self.subscribers:
            await self.bot.send_message(subscriber, message)

    async def start(self) -> None:
        # Run the bot until you press Ctrl-C.
        await self.bot.start()


async def main():
    """Start the bot."""
    # Connect the bot to number.
    async with Bot(os.environ["SIGNAL_PHONE_NUMBER"]) as bot:
        await NewsletterBot(bot).start()


if __name__ == '__main__':
    import anyio

    anyio.run(main)
