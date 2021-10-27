import os

import requests
import dotenv
import isodate
import requests_cache

requests_cache.install_cache('youtube')

dotenv.load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
API_KEY = os.environ.get('API_KEY')


def format_time(seconds, days=False):
    if days:
        d, s = divmod(seconds, 86400)
        h, s = divmod(s, 3600)
        m, s = divmod(s, 60)

    h, s = divmod(seconds, 3600)
    m, s = divmod(s, 60)
    return f'{h:02.0f}:{m:02.0f}:{s:02.0f}'  # format for now


def format_result():
    pass


def get_duration(item_ids) -> float:
    """Accept a list of item ids and return their total duration."""
    url = 'https://www.googleapis.com/youtube/v3/videos'

    params = {
        'key': API_KEY,
        'part': ['contentDetails'],
        'id': ','.join(item_ids),
        'fields': 'items/contentDetails/duration',
    }

    r = requests.get(url, params=params)
    items = r.json().get('items')
    if items:
        durations = [
            isodate.parse_duration(
                i['contentDetails']['duration']
            ).total_seconds()
            for i in items
        ]
        return sum(durations)
    return 0


def get_result(playlist_id):
    """Calculate playlist duration.

    Return playlist/album duration as a formatted string based on a valid id.
    In case of an invalid id return an API error message or an empty string.
    """
    url = 'https://www.googleapis.com/youtube/v3/playlistItems'
    params = {
        'key': API_KEY,
        'part': ['snippet', 'contentDetails'],
        'playlistId': playlist_id,
        'maxResults': 50,
        'fields': 'nextPageToken,items/snippet(resourceId/videoId)',
        'pageToken': '',
    }
    total_duration = 0

    while True:
        r = requests.get(url, params=params)
        data = r.json()

        if not data.get('items'):
            if data.get('error'):
                return {'error': data.get('error').get('message')}
            else:
                return {}

        item_ids = [
            v['snippet']['resourceId']['videoId'] for v in data['items']
        ]
        total_duration += get_duration(item_ids)
        next_page_token = data.get('nextPageToken')

        if not next_page_token:
            break
        params['pageToken'] = next_page_token

    return {'duration': format_time(total_duration)}
