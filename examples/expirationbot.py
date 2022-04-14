#!/usr/bin/env python
#
# Semaphore: A simple (rule-based) bot library for Signal Private Messenger.
# Copyright (C) 2022 Lazlo Westerhof <semaphore@lazlo.me>
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
Signal Bot example, sets the message expiration timer for a chat to random value.
"""
import os
import random

from semaphore import Bot, ChatContext


async def expiration(ctx: ChatContext) -> None:
    if not ctx.message.empty():
        await ctx.message.mark_read()

        receiver = ctx.message.get_group_id()
        if receiver is None:
            receiver = ctx.message.source.uuid

        await ctx.bot.set_expiration(receiver, random.randint(0, 59))


async def main() -> None:
    """Start the bot."""
    # Connect the bot to number.
    async with Bot(os.environ["SIGNAL_PHONE_NUMBER"]) as bot:
        bot.register_handler("", expiration)

        # Run the bot until you press Ctrl-C.
        await bot.start()


if __name__ == '__main__':
    import anyio
    anyio.run(main)
