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
Signal Bot example, replies with latest XKCD comic.
"""
import os
from pathlib import Path

import anyio
import asks  # type: ignore
import feedparser  # type: ignore
from bs4 import BeautifulSoup  # type: ignore

from semaphore import Bot, ChatContext


async def xkcd(ctx: ChatContext) -> None:
    path = Path(__file__).parent.absolute() / "tmp" / "tmp_xkcd.png"

    Feed = feedparser.parse((await asks.get('https://xkcd.com/rss.xml')).text)
    pointer = Feed.entries[0]
    soup = BeautifulSoup(pointer.description, "html.parser")

    for img in soup.find_all("img"):
        comic = img["src"]
        description = img["title"]

    r = await asks.get(comic, stream=True)
    async with await anyio.open_file(path, "wb") as f:
        async for chunk in r.body:
            await f.write(chunk)

    message = f"{pointer.title} - {description} ({pointer.link})"
    attachment = {"filename": str(path),
                  "width": "100",
                  "height": "100"}

    await ctx.message.reply(body=message, attachments=[attachment])


async def main():
    """Start the bot."""
    # Connect the bot to number.
    async with Bot(os.environ["SIGNAL_PHONE_NUMBER"]) as bot:
        bot.register_handler("!xkcd", xkcd)

        # Run the bot until you press Ctrl-C.
        await bot.start()


if __name__ == '__main__':
    anyio.run(main)
