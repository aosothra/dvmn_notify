# dvmn_notify

This script implements client side of long-polling communication with [dvmn.org API](https://dvmn.org/api/docs/) in order to get code review status updates. 

## Installation guidelines


You must have Python3 installed on your system.
You may use `pip` (or `pip3` to avoid conflict with Python2) to install dependencies.
```
pip install -r requirements.txt
```
It is strongly advised to use [virtualenv/venv](https://docs.python.org/3/library/venv.html) for project isolation.

This script uses `.env` file in root folder to store variables neccessary for operation. So, do not forget to create one!

Inside your `.env` file you can specify following settings:

| Key | Type | Default (if optional) | Description |
| - | - | - | - |
| `DVMN_API_TOKEN` | `str` |  | Your Devman API Token that is required for authorization. [(See Devman API doc)](https://dvmn.org/api/docs/)
| `TG_BOT_TOKEN` | `str` |  | Your Telegram bot token to access the Telegram HTTP API. [(See Telegram bot doc)](https://core.telegram.org/bots#6-botfather)
| `TG_CHAT_ID` | `int` |  | Your Telegram chat guid.
| `VERBOSE` | `bool` | `False` | Flag for verbose terminal output.



## Basic usage (for the lack of any other...)

```
py main.py 
```

Once run, this script will keep polling dvmn API indefinitely. Flag `VERBOSE` as `True` if you want to see execution details. Upon update from the server, the script will send a Telegram message to the specified chat with a notification.

## Bulding image and running as a container

This project contains `Dockerfile` which lets you create docker image and run your python application as a container.

Make sure you have docker [installed](https://docs.docker.com/get-started/#download-and-install-docker).

```sh
docker --version
```

From `root` of your cloned repo build an image using following command:
```sh
docker build --tag dvmn-notify .
```

Once the process is complete, you can run it as a detached container. Make sure you've set up your `.env` file as described above, and run following command:

```sh
docker run -dp 80:80 --env-file .env dvmn-notify
```

### Project goals

This project was created for educational purposes as part of [dvmn.org](https://dvmn.org/) Backend Developer course.