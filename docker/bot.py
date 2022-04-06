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
Signal Bot example, tells everyone it is a bot running in a Docker container!
"""
import os
import random

from semaphore import Bot, ChatContext


async def docker(ctx: ChatContext) -> None:
    if 'known_receiver' in ctx.data:
        emoji = ['❤️', '🔥', '👍', '💩', '🐰']
        await ctx.message.reply(random.choice(emoji), reaction=True)
    else:
        ctx.data['known_receiver'] = True
        await ctx.message.reply('👋', reaction=True)
        await ctx.message.reply("Hi! I'm a Signal bot running in a Docker container!",
                                quote=False)


async def main():
    """Start the bot."""
    # Connect the bot to number.
    async with Bot(os.environ["SIGNAL_PHONE_NUMBER"]) as bot:
        bot.register_handler("", docker)

        # Run the bot until you press Ctrl-C.
        await bot.start()


if __name__ == '__main__':
    import anyio
    anyio.run(main)
