#!/usr/bin/env python
#
# Semaphore: A simple (rule-based) bot library for Signal Private Messenger.
# Copyright (C) 2020-2022 Lazlo Westerhof <semaphore@lazlo.me>
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
Signal Bot example, repeats received messages in sPOngEbOb sqUArepAnTs text.
"""
import os

from semaphore import Bot, ChatContext


async def spongebob(ctx: ChatContext) -> None:
    from random import choice
    from random import seed

    orig = ctx.message.get_body()
    seed(orig)
    await ctx.message.reply(''.join(choice((ch.lower, ch.upper))() for ch in orig))


async def main() -> None:
    """Start the bot."""
    # Connect the bot to number.
    async with Bot(os.environ["SIGNAL_PHONE_NUMBER"]) as bot:
        bot.register_handler("", spongebob)

        # Run the bot until you press Ctrl-C.
        await bot.start()


if __name__ == '__main__':
    import anyio
    anyio.run(main)
