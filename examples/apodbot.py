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
Signal Bot example, replies with Astronomy Picture of the Day.
"""
import os
from pathlib import Path

import anyio
import asks  # type: ignore
import feedparser  # type: ignore
from bs4 import BeautifulSoup  # type: ignore

from semaphore import Bot, ChatContext, Attachment


async def apod(ctx: ChatContext) -> None:
    path = Path(__file__).parent.absolute() / "tmp" / "tmp_apod.jpg"
    content = (await asks.get('https://apod.nasa.gov/apod.rss')).text
    Feed = feedparser.parse(content)
    pointer = Feed.entries[0]
    soup = BeautifulSoup(pointer.description, "html.parser")

    for img in soup.find_all("img"):
        apod = img["src"]
        description = img["alt"]

    r = await asks.get(apod, stream=True)
    async with await anyio.open_file(path, "wb") as f:
        async for chunk in r.body:
            await f.write(chunk)

    message = f"{pointer.title} - {description} (https://apod.nasa.gov/apod/)"
    attachment = Attachment(str(path), width=100, height=100)

    await ctx.message.reply(body=message, attachments=[attachment])


async def main():
    """Start the bot."""
    # Connect the bot to number.
    async with Bot(os.environ["SIGNAL_PHONE_NUMBER"]) as bot:
        bot.register_handler("!apod", apod)

        # Run the bot until you press Ctrl-C.
        await bot.start()


if __name__ == '__main__':
    anyio.run(main)
