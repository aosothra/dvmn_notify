import logging
import time
import requests
import telegram

from environs import Env


log = logging.getLogger(__file__)


class TelegramLogHandler(logging.Handler):
    def __init__(self, bot, chat_id):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)

        self.bot.send_message(
            chat_id=self.chat_id,
            text=log_entry
        )
    


def main():
    env = Env()
    env.read_env()
    chat_id = env.int('TG_CHAT_ID')

    logging.basicConfig(level=logging.INFO)
    if env.bool('VERBOSE', False):
        log.setLevel(logging.DEBUG)

    bot = telegram.Bot(env('TG_BOT_TOKEN'))

    log.addHandler(
        TelegramLogHandler(bot, chat_id)
    )


    dvmn_api_token = env('DVMN_API_TOKEN')    

    url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': f'Token {dvmn_api_token}'
    }
    params = None

    log.info(f'Notification bot is running now.')
    while True:        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            review_data = response.json()
            if review_data['status'] == 'timeout':
                log.debug('No updates from server. Keep polling...')
                params = {'timestamp': review_data['timestamp_to_request']}
            elif review_data['status'] == 'found':
                log.debug('New update from server!')

                for attempt in review_data['new_attempts']:
                    notification = (
                            f"Our submission to lesson '{attempt['lesson_title']}' recieved a review.\n{attempt['lesson_url']}"
                            if attempt['is_negative'] else
                            f"Our submission to lesson '{attempt['lesson_title']}' was accepted with no remarks!\n{attempt['lesson_url']}"
                        )
                    bot.send_message(
                        chat_id=chat_id,
                        text=notification
                    )
                params = {'timestamp': review_data['last_attempt_timestamp'] + 0.001}

                log.debug('Keep polling...')
            else:
                log.debug(f'Response status {review_data["status"]} is not accounted for. Keep polling...')
                params = None
        except requests.exceptions.ReadTimeout:
            log.warning('Request timed out. Keep polling...')
        except requests.exceptions.ConnectionError:
            log.warning('Failed to connect. Next attempt in 90s.')
            time.sleep(90)
            log.debug('Resume polling...')
        except Exception:
            log.exception("An exception encountered while running.")


if __name__ == '__main__':
    main()
