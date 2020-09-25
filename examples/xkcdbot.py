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
import urllib.request
from pathlib import Path

import feedparser  # type: ignore
from bs4 import BeautifulSoup  # type: ignore

from semaphore import Bot, ChatContext


def xkcd(context: ChatContext) -> None:
    context.message.mark_read()

    path = Path(__file__).parent.absolute()
    Feed = feedparser.parse('https://xkcd.com/rss.xml')
    pointer = Feed.entries[0]
    soup = BeautifulSoup(pointer.description, "html.parser")

    for img in soup.find_all("img"):
        comic = img["src"]
        description = img["title"]

    urllib.request.urlretrieve(comic, f"{path}/tmp/tmp_xkcd.png")

    message = f"{pointer.title} - {description} ({pointer.link})"
    attachment = {"filename": f"{path}/tmp/tmp_xkcd.png",
                  "width": "100",
                  "height": "100"}

    context.message.reply(body=message, attachments=[attachment])


def main():
    """Start thfee bot."""
    # Connect the bot to number.
    bot = Bot("+xxxxxxxxxxx")

    # Add handler to bot.
    bot.register_handler("!xkcd", xkcd)

    # Run the bot until you press Ctrl-C.
    bot.start()


if __name__ == '__main__':
    main()
