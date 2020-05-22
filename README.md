# Semaphore
A simple (rule-based) bot library for [Signal](https://signal.org/) Private Messenger in Python.

## Requirements
- Python 3.6+
- [signald 0.9.0+](https://gitlab.com/thefinn93/signald), a daemon that facilitates communication over [Signal](https://signal.org/)

## Installation
1. Install signald or build from source
    ```bash
    $ git clone https://gitlab.com/thefinn93/signald.git
    $ cd signald
    $ make installDist
    $ make setup
    ```

2. Install Semaphore

    With pip:
    ```bash
    $ pip install semaphore
    ```

    From source:
    ```bash
    $ git clone https://github.com/lwesterhof/semaphore.git
    $ cd semaphore
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
{"type": "send", "username": "+xxxxxxxxxxx", "recipientNumber": "+yyyyyyyyyyy", "messageBody": "Hello world"}
```

6. Subscribe to receive messages for the bot by sending following message on the control socket (replace `+xxxxxxxxxxx` with bot Signal number)
```json
{"type": "subscribe", "username": "+xxxxxxxxxxx"}
```

7. Open a new terminal, edit the example echo bot and replace `+xxxxxxxxxxx` with the Signal bot number:
```bash
$ cd semaphore/examples/
$ vim echobot.py
```

8. Start the example echo bot
```bash
$ python echobot.py
```

9. Send message to Signal bot running on `+xxxxxxxxxxx` and wait for an echo

10. Now you can start writing your own bot for [Signal](https://signal.org/) Private Messenger!

## Code example
```python
from semaphore import Bot, Message, Reply

def echo(message: Message, match) -> Reply:
    return Reply(message=message.get_text())

def main():
    """Start the bot."""
    # Connect the bot to number.
    bot = Bot("+xxxxxxxxxxx")

    # Add handler to bot.
    bot.register_handler("", echo)

    # Run the bot until you press Ctrl-C.
    bot.start()

if __name__ == '__main__':
    main()
```

## Example bots
The following example bots can be found in [examples](examples):
- [apodbot](examples/apodbot.py), replies with Astronomy Picture of the Day
- [bbcbot](examples/bbcbot.py), replies with latest BBC headlines
- [echobot](examples/echobot.py), repeats received messages
- [spongebot](examples/spongebot.py), repeats received messages in sPOngEbOb sqUArepAnTs text
- [quotebot](examples/quotebot.py), quotes and repeats received messages
- [xkcdbot](examples/xkcdbot.py), replies with latest XKCD comic

## History
### v0.2.0
* Support for quoting messages.

### v0.1.0
* First release on Github.

## License
This project is licensed under the GPL-v3 license.
The full license can be found in [LICENSE.txt](LICENSE.txt).
