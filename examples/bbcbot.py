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
Signal Bot example, replies with latest BBC headlines.
"""
import os
import re

import asks  # type: ignore
import feedparser  # type: ignore

from semaphore import Bot, ChatContext


async def bbc_info(ctx: ChatContext) -> None:
    info = """BBC News Bot

!bbc world    - BBC World news
!bbc business - BBC Business news
!bbc politics - BBC Politics news
!bbc tech     - BBC Technology news"""

    await ctx.message.reply(body=info)


FEEDS = {
    "world": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "politics": "http://feeds.bbci.co.uk/news/politics/rss.xml",
    "business": "http://feeds.bbci.co.uk/news/business/rss.xml",
    "tech": "http://feeds.bbci.co.uk/news/technology/rss.xml",
}

DEFAULT_FEED = "http://feeds.bbci.co.uk/news/rss.xml"


async def bbc_feed(ctx: ChatContext) -> None:
    # Find out which news feed to parse.
    news = ctx.match.group(1)
    feed = FEEDS.get(news, DEFAULT_FEED)

    # Parse news feed.
    Feed = feedparser.parse((await asks.get(feed)).text)

    # Create message with 3 latest headlines.
    reply = []
    for x in range(3):
        pointer = Feed.entries[x]
        reply.append(f"{pointer.title} ({pointer.link})")
        if x < 2:
            reply.append("\n")

    await ctx.message.reply("\n".join(reply))


async def main() -> None:
    """Start the bot."""
    # Connect the bot to number.
    async with Bot(os.environ["SIGNAL_PHONE_NUMBER"]) as bot:
        bot.register_handler("!bbc info", bbc_info)
        bot.register_handler(re.compile("!bbc (.*)"), bbc_feed)
        bot.register_handler("!bbc", bbc_feed)

        # Run the bot until you press Ctrl-C.
        await bot.start()


if __name__ == '__main__':
    import anyio
    anyio.run(main)
