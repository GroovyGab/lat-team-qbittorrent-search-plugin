# VERSION: 1.0
# AUTHORS: GroovyGab (ghernandezlohaus.78@gmail.com)


import json
import os
from datetime import datetime
from urllib.parse import unquote, urlencode

from helpers import retrieve_url
from novaprinter import prettyPrinter

CONFIG_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lat_team.json')
CONFIG_DATA = {'api_token': 'YOUR_API_TOKEN'}


def load_config():
    global CONFIG_DATA

    try:
        with open(CONFIG_PATH, 'r') as file:
            CONFIG_DATA = json.load(file)
    except FileNotFoundError:
        save_config()
    except Exception as error:
        CONFIG_DATA = {'error': str(error)}
        save_config()


def save_config():
    with open(CONFIG_PATH, 'w') as file:
        file.write(json.dumps(CONFIG_DATA, sort_keys=True, indent=2))


load_config()


def iso_to_timestamp(iso_date: str) -> int:
    return int(datetime.fromisoformat(iso_date).timestamp())


class lat_team(object):
    url = 'https://lat-team.com'
    api_token = CONFIG_DATA['api_token']
    errored = 'error' in CONFIG_DATA
    name = 'Lat-Team'
    sort_by = 'seeders'
    items_per_page = '100'
    supported_categories = {
        'all': '0',
        'anime': '5',
        'games': '4',
        'movies': '1',
        'music': '3',
        'software': '17',
        'tv': '2',
    }

    def search(self, what: str, cat: str = 'all'):
        what = unquote(what)
        category = self.supported_categories[cat.lower()]

        if self.errored:
            self.handle_error("There's been a problem with the configuration file. Check lat_team.json for details.")
            return

        params = {
            'api_token': self.api_token,
            'name': what,
            'sortField': self.sort_by,
            'perPage': self.items_per_page,
        }

        if category != '0':
            params['categories[]'] = category

        response = retrieve_url(f'https://lat-team.com/api/torrents/filter?{urlencode(params)}')

        if '<title>Login - Lat-Team</title>' in response:
            self.handle_error('API token is not set or invalid. See description page for details.')
            return

        response_json = json.loads(response)

        for torrent_data in response_json['data']:
            result = {
                'link': torrent_data['attributes']['download_link'],
                'name': torrent_data['attributes']['name'],
                'size': torrent_data['attributes']['size'],
                'seeds': torrent_data['attributes']['seeders'],
                'leech': torrent_data['attributes']['leechers'],
                'engine_url': self.url,
                'desc_link': torrent_data['attributes']['details_link'],
                'pub_date': iso_to_timestamp(torrent_data['attributes']['created_at']),
            }

            prettyPrinter(result)

    def handle_error(self, error: str):
        result = {
            'link': self.url,
            'name': error,
            'size': -1,
            'seeds': -1,
            'leech': -1,
            'engine_url': self.url,
            'desc_link': 'https://github.com/GroovyGab/lat-team-qbittorrent-search-plugin',
        }

        prettyPrinter(result)
