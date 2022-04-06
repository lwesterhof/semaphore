# Run a Signal Bot in a Docker container
This document describes the steps to run a Signal Bot written with Semaphore in a Docker container.

## Dependencies
* [git](https://git-scm.com/)
* [Docker](https://www.docker.com/)
* [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) (when deploying to Heroku)

## Clone Semaphore repository
Clone the Semaphore repository and change directory to the docker directory.
```bash
git clone https://github.com/lwesterhof/semaphore.git
cd semaphore/docker/
```

## Deploy bot container
Deploy bot container local or to Heroku.

### Local
1. Build Docker container
    ```bash
    docker build -t semaphore-bot .
    ```

2.  Run Docker container (replace `<container_name>` with container name)
    ```bash
    docker run -d --name <container_name> semaphore-bot
    ```

3. Attach to container (replace `<container_name>` with container name)
    ```bash
    docker exec -it <container_name> bash
    ```

### Heroku
1. Create Heroku app (replace `<app_name>` with app name)
    ```bash
    heroku container:login
    heroku create <app_name>
    ```

2.  Push and release container (replace `<app_name>` with app name)
    ```bash
    heroku container:push worker --app <app_name>
    heroku container:release worker --app <app_name>
    ```

3. Attach to container (replace `<app_name>` with app name)
    ```bash
    heroku run bash -a <app_name>
    ```

## Register Signal account and start the bot
1. Download [Signal Captcha Helper](https://gitlab.com/signald/captcha-helper) and complete Signal captcha on local machine
    ```bash
    wget -O signal-captcha-helper https://gitlab.com/api/v4/projects/27947268/jobs/artifacts/main/raw/signal-captcha-helper?job=build%3Aamd64
    chmod +x signal-captcha-helper
    ./signal-captcha-helper
    ```

2. Register account with captcha (replace `+xxxxxxxxxxx` with bot Signal number and `<captcha>` with captcha from previous step)
    ```bash
    signaldctl account register +xxxxxxxxxxx --captcha <captcha>
    ```

3. Verify account with verfication code (replace `+xxxxxxxxxxx` with bot Signal number and `<verfication_code>` with received Signal verfication code)
    ```bash
    signaldctl account verify +xxxxxxxxxxx <verfication_code>
    ```

4. Check that account is registered
    ```bash
    signaldctl account list
    ```

5. Start the bot (replace `+xxxxxxxxxxx` with bot Signal number)
    ```bash
    /usr/bin/bash /root/start_bot.sh +xxxxxxxxxxx &> /var/log/semaphore.log &
    ```

6. Check if bot is running
    ```bash
    tail -f /var/log/semaphore.log
    ```
