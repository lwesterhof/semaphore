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
Signal Bot example, checks the BTC price and sends a
notification if it drops below a set price.
"""
import json
import re
import urllib.request
from time import time
from typing import Optional

from semaphore import Bot, ChatContext


def check_price(context: ChatContext) -> None:
    url = "https://blockchain.info/ticker"
    request = urllib.request.Request(url)

    response = urllib.request.urlopen(request).read()
    content = json.loads(response.decode('utf-8'))

    price = int(context.match.group(1))
    last_price = int(content['USD']['last'])

    if int(content['USD']['last']) < price:
        if 'job' in context.data:
            old_job = context.data["job"]
            old_job.schedule_removal()

        notification = f"BTC price dropped below ${price}!\nCurrent price: ${last_price}"
        context.message.reply(body=notification)


def set_notification(context: ChatContext) -> None:
    try:
        now = time()
        price = int(context.match.group(1))

        if price < 0:
            raise Exception

        job = context.job_queue.run_repeating(now, check_price, context, 5 * 60)
        context.data["job"] = job

        context.message.mark_read()
        context.message.reply(body="BTC price check set!")
    except Exception:
        context.message.mark_read()
        context.message.reply(body="Usage: !btc <dollars>")


def unset_notification(context: ChatContext) -> None:
    if 'job' in context.data:
        old_job = context.data["job"]
        old_job.schedule_removal()

    context.message.mark_read()
    context.message.reply(body="BTC price check unset!")


def main():
    """Start the bot."""
    # Connect the bot to number.
    bot = Bot("+xxxxxxxxxxx")

    # Add btc handlers.
    bot.register_handler(re.compile("!btc unset"), unset_notification)
    bot.register_handler(re.compile("!btc (.*)"), set_notification)

    # Run the bot until you press Ctrl-C.
    bot.start()


if __name__ == '__main__':
    main()
