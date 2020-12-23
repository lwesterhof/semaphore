# Semaphore [![PyPI](https://img.shields.io/pypi/v/semaphore-bot)](https://pypi.org/project/semaphore-bot/) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/lwesterhof/semaphore/Python) ![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/lwesterhof/semaphore) ![GitHub](https://img.shields.io/github/license/lwesterhof/semaphore)

A simple (rule-based) bot library for [Signal](https://signal.org/) Private Messenger in Python.

## Table of contents
   * [Requirements](#requirements)
   * [Installation](#installation)
   * [Quick start](#quick-start)
   * [Demo](#demo)
   * [Code example](#code-example)
   * [Example bots](#example-bots)
   * [Changelog](#changelog)
   * [License](#license)

## Requirements
- ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/semaphore-bot)
- [signald](https://gitlab.com/thefinn93/signald) 0.11.1+ ([7ef8166d](https://gitlab.com/thefinn93/signald/-/commit/7ef8166d7cc12be96818dfc4480da01994dd7be4) or later), a daemon that facilitates communication over [Signal](https://signal.org/)

## Installation
1. Install signald or build from source
    ```bash
    $ git clone https://gitlab.com/thefinn93/signald.git
    $ cd signald
    $ make installDist
    $ make setup
    ```

2. Install Semaphore

    Latest release from PyPi:
    ```bash
    $ pip install semaphore-bot
    ```

    From source with pip:
    ```bash
    $ pip install git+https://github.com/lwesterhof/semaphore.git
    ```

    From source:
    ```bash
    $ git clone https://github.com/lwesterhof/semaphore.git
    $ cd semaphore
    $ python -m pip install .
    $ python setup.py sdist bdist_wheel
    $ python -m pip install dist/semaphore-*.tar.gz
    ```

## Quick start
1. Start signald
    ```bash
    $ cd signald
    $ build/install/signald/bin/signald
    ```

2. Open a new terminal and connect to signald control socket
    ```bash
    nc -U /var/run/signald/signald.sock
    ```

3. Register phone number with Signal by sending following message on the control socket (replace `+xxxxxxxxxxx` with bot Signal number)
    ```json
    {"type": "register", "username": "+xxxxxxxxxxx"}
    ```

4. Verify phone number with SMS verification code by sending following message on the control socket (replace `+xxxxxxxxxxx` with bot Signal number and `zzz-zzz` with verification code)
    ```json
    {"type": "verify", "username": "+xxxxxxxxxxx", "code": "zzz-zzz"}
    ```

5. Verify Signal is working by sending following message on the control socket (replace `+xxxxxxxxxxx` with bot Signal number and `+yyyyyyyyyyy` with your Signal number)
    ```json
    {"type": "send", "username": "+xxxxxxxxxxx", "recipientAddress": {"number": "+yyyyyyyyyyy"}, "messageBody": "Hello world"}
    ```

6. Subscribe to receive messages for the bot by sending following message on the control socket (replace `+xxxxxxxxxxx` with bot Signal number)
    ```json
    {"type": "subscribe", "username": "+xxxxxxxxxxx"}
    ```

7. Open a new terminal and set the `SIGNAL_PHONE_NUMBER` environment variable to your phone number:
    ```bash
    $ export SIGNAL_PHONE_NUMBER=+xxxxxxxxxxx
    ```

8. Start the example echo bot
    ```bash
    $ python echobot.py
    ```

9. Send message to Signal bot running on `+xxxxxxxxxxx` and wait for an echo

10. Now you can start writing your own bot for [Signal](https://signal.org/) Private Messenger!

## Demo
A demonstration bot is running on `+31686100384`.
Do not send anything confidential, use at your own risk!
![Conversation with demonstration bot](demo.jpg)

## Code example
```python
import anyio
from semaphore import Bot, ChatContext

# Connect the bot to number.
bot = Bot("+xxxxxxxxxxx")

@bot.handler('')
async def echo(ctx: ChatContext) -> None:
    await ctx.message.reply(ctx.message.get_body())

async def main():
    async with bot:
        # Run the bot until you press Ctrl-C.
        await bot.start()

anyio.run(main)
```

## Example bots
The following example bots can be found in [examples](examples):
- [apodbot](examples/apodbot.py), replies with Astronomy Picture of the Day
- [bbcbot](examples/bbcbot.py), replies with latest BBC headlines
- [btcbot](examples/btcbot.py), sends notification when BTC price drops below a set price
- [echobot](examples/echobot.py), repeats received messages
- [lovebot](examples/lovebot.py), loves everything you say!
- [spongebot](examples/spongebot.py), repeats received messages in sPOngEbOb sqUArepAnTs text
- [stickerbot](examples/stickerbot.py), links to the sticker pack for received stickers
- [timerbot](examples/timerbot.py), sends an alert after a predefined time
- [quotebot](examples/quotebot.py), quotes and repeats received messages
- [xkcdbot](examples/xkcdbot.py), replies with latest XKCD comic

## Changelog
**v0.9.1**
* Fix repeating job re-add to queue (thanks @grandchild)

**v0.9.0**
* Support for typing indicators
* Support for GroupsV2 (thanks @thefinn93)
* Example sticker bot (thanks @iomintz)
* Compatibility with signald 0.11.0+

**v0.8.0**
* Support for Python 3.9
* Support for executing multiple handlers in parallel (thanks @iomintz)
* Support incoming sticker messages (thanks @iomintz)

**v0.7.1**
* Support for decorators to register handlers
* Support for sending delivery receipts
* Mark messages as read by default

**v0.7.0**
* Compatibility with signald 0.10.0+
* Support for multiple replies/reactions by handler (thanks @iomintz)
* Marking messages as read is optional
* First release on PyPi

**v0.6.0**
* Support for message reactions
* Example message reaction bot

**v0.5.0**
* Improve the logging system
* Add logging to job queue
* Strict typing

**v0.4.0**
* Support for recurring jobs
* Example BTC price notification bot

**v0.3.0**
* Support for scheduled jobs
* Example timer bot

**v0.2.0**
* Support for quoting messages
* Example quote bot

**v0.1.0**
* First release on Github

## License
This project is licensed under the AGPL-v3 license.
The full license can be found in [LICENSE.txt](LICENSE.txt).
