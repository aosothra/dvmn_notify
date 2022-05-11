import logging
import requests
import telegram

from environs import Env


def init_logger():
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    terminal_handler = logging.StreamHandler()
    terminal_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    terminal_handler.setFormatter(terminal_formatter)

    log.addHandler(terminal_handler)


def send_bot_notification(bot, chat_id, lesson_title, lesson_url, is_negative):
    text = (
        f"На нашу работу по уроку '{lesson_title}' пришли замечания.\n{lesson_url}"
        if is_negative else
        f"Наша работа по уроку '{lesson_title}' принята без замечаний.\n{lesson_url}"
    )
    bot.send_message(chat_id=chat_id, text=text)


def main():
    env = Env()
    env.read_env()

    init_logger()
    log = logging.getLogger(__name__)

    bot = telegram.Bot(env('TG_BOT_TOKEN'))
    chat_id = env.int('TG_CHAT_ID')

    dvmn_api_token = env('DVMN_API_TOKEN')    

    url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': f'Token {dvmn_api_token}'
    }
    params = None

    log.info(f'Polling {url}')
    while True:        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            log.warning('Request timed out. Keep polling...')
            continue
        except requests.exceptions.ConnectionError:
            log.warning('Failed to connect. Keep polling...')
            continue

        response_data = response.json()
        if response_data['status'] == 'timeout':
            log.info('No updates from server. Keep polling...')
            params = {'timestamp': response_data['timestamp_to_request']}
        elif response_data['status'] == 'found':
            log.info('New Update from server:', response_data)

            for attempt in response_data['new_attempts']:
                send_bot_notification(
                    bot,
                    chat_id,
                    attempt['lesson_title'],
                    attempt['lesson_url'],
                    attempt['is_negative']
                    )
            params = {'timestamp': response_data['last_attempt_timestamp'] + 0.001}

            log.info('Keep polling...')
        else:
            log.warning(f'Response status {response_data["status"]} is not accounted for.')
            params = None
            log.info('Keep polling...')

if __name__ == '__main__':
    main()