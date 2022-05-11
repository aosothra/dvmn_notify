import logging
import requests

from environs import Env


def init_logger():
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    terminal_handler = logging.StreamHandler()
    terminal_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    terminal_handler.setFormatter(terminal_formatter)

    log.addHandler(terminal_handler)


def main():
    env = Env()
    env.read_env()

    init_logger()
    log = logging.getLogger(__name__)

    token = env('DVMN_API_TOKEN')

    url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': f'Token {token}'
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
        else:
            log.info('New Update from server:', response_data)
            log.info('Keep polling...')
            params = {'timestamp': response_data['last_attempt_timestamp'] + 0.001}

if __name__ == '__main__':
    main()