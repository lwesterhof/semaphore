# Run a Signal Bot in a Docker container
This document describes the steps to run a Signal Bot written with Semaphore in a Docker container.
The example will deploy a [demo bot](bot.py), you can change this bot or copy another bot in the [Dockerfile](Dockerfile).

## Dependencies
* [git](https://git-scm.com/)
* [Docker](https://www.docker.com/)
* [Docker Compose](https://github.com/docker/compose)

## Deploy the bot
1. Clone the Semaphore repository and change directory to the docker directory.
    ```bash
    git clone https://github.com/lwesterhof/semaphore.git
    cd semaphore/docker/
    ```

2. Set phone number of the bot (replace +xxxxxxxxxxx with phone number).
    ```bash
    export SIGNAL_PHONE_NUMBER=+xxxxxxxxxxx
    ```

3. Deploy Docker container with signald.
    ```bash
    docker-compose up -d signald
    ```

4. Download [Signal Captcha Helper](https://gitlab.com/signald/captcha-helper) and complete Signal captcha on local machine.
    ```bash
    wget -O signal-captcha-helper https://gitlab.com/api/v4/projects/27947268/jobs/artifacts/main/raw/signal-captcha-helper?job=build%3Aamd64
    chmod +x signal-captcha-helper
    ./signal-captcha-helper
    ```

5. Attach to container running signald.
    ```bash
    docker exec -it signald bash
    ```

6. Register account with captcha (replace `+xxxxxxxxxxx` with phone number and `<captcha>` with captcha from step 4).
    ```bash
    signaldctl account register +xxxxxxxxxxx --captcha <captcha>
    ```

7. Verify account with verfication code (replace `+xxxxxxxxxxx` with bot Signal number and `<verfication_code>` with received Signal verfication code).
    ```bash
    signaldctl account verify +xxxxxxxxxxx <verfication_code>
    ```

8. Check that account is registered.
    ```bash
    signaldctl account list
    ```

9. Exit signald Docker container.
    ```bash
    exit
    ```

10. Deploy Docker container with the bot and start the bot.
    ```bash
    docker-compose up
    ```
