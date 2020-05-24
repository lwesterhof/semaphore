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
Signal Bot example, includes several example bots.
"""
import re
from time import time

from semaphore import Bot, Message, Reply


def alarm(message: Message) -> Reply:
    return Reply(message="Beep! Beep! Beep!")


def set_timer(message: Message, match, jobqueue) -> Reply:
    try:
        delta = int(match.group(1))
        alarm_time = time() + delta
        jobqueue.put(alarm_time, alarm, message)
        return Reply(message="Timer set!")
    except Exception:
        return Reply(message="Setting timer failed.")


def main():
    """Start the bot."""
    # Connect the bot to number.
    bot = Bot("+xxxxxxxxxxx", debug=True)

    # Add timer handler.
    bot.register_handler(re.compile("!timer (.*)"), set_timer, job=True)

    # Run the bot until you press Ctrl-C.
    bot.start()


if __name__ == '__main__':
    main()
