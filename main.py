import logging
import requests
import telegram

from environs import Env


log = logging.getLogger(__file__)


def main():
    env = Env()
    env.read_env()

    logging.basicConfig(level=logging.WARNING)
    if env.bool('VERBOSE', False):
        log.setLevel(logging.DEBUG)

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

        review_data = response.json()
        if review_data['status'] == 'timeout':
            log.info('No updates from server. Keep polling...')
            params = {'timestamp': review_data['timestamp_to_request']}
        elif review_data['status'] == 'found':
            log.info('New update from server! Sending notification over telegram.')

            for attempt in review_data['new_attempts']:
                text = (
                        f"На нашу работу по уроку '{attempt['lesson_title']}' пришли замечания.\n{attempt['lesson_url']}"
                        if attempt['is_negative'] else
                        f"Наша работа по уроку '{attempt['lesson_title']}' принята без замечаний.\n{attempt['lesson_url']}"
                    )
                bot.send_message(chat_id=chat_id, text=text)
            params = {'timestamp': review_data['last_attempt_timestamp'] + 0.001}

            log.info('Keep polling...')
        else:
            log.warning(f'Response status {review_data["status"]} is not accounted for.')
            params = None
            log.info('Keep polling...')


if __name__ == '__main__':
    main()
