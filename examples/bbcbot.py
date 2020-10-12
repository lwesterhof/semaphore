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
Signal Bot example, replies with latest BBC headlines.
"""
import re

import feedparser  # type: ignore

from semaphore import Bot, ChatContext


def bbc_info(ctx: ChatContext) -> None:
    info = """BBC News Bot

!bbc world    - BBC World news
!bbc business - BBC Business news
!bbc politics - BBC Politics news
!bbc tech     - BBC Technology news"""

    ctx.message.reply(body=info)


def bbc_feed(ctx: ChatContext):
    # Find out which news feed to parse.
    try:
        news = ctx.match.group(1)
        if news == "world":
            feed = "http://feeds.bbci.co.uk/news/world/rss.xml"
        elif news == "politics":
            feed = "http://feeds.bbci.co.uk/news/politics/rss.xml"
        elif news == "business":
            feed = "http://feeds.bbci.co.uk/news/business/rss.xml"
        elif news == "tech":
            feed = "http://feeds.bbci.co.uk/news/technology/rss.xml"
        else:
            feed = "http://feeds.bbci.co.uk/news/rss.xml"
    except Exception:
        feed = "http://feeds.bbci.co.uk/news/rss.xml"

    # Parse news feed.
    Feed = feedparser.parse(feed)

    # Create message with 3 latest headlines.
    reply = ""
    for x in range(0, 3):
        pointer = Feed.entries[x]
        reply += f"{pointer.title} ({pointer.link})"
        if x < 2:
            reply += "\n\n"

    ctx.message.reply(reply)


def main():
    """Start the bot."""
    # Connect the bot to number.
    bot = Bot("+xxxxxxxxxxx")

    # Add handlers to bot.
    bot.register_handler("!bbc info", bbc_info)
    bot.register_handler(re.compile("!bbc (.*)"), bbc_feed)
    bot.register_handler("!bbc", bbc_feed)

    # Run the bot until you press Ctrl-C.
    bot.start()


if __name__ == '__main__':
    main()
