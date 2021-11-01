import os

import requests
import dotenv
import isodate
import requests_cache

requests_cache.install_cache('youtube')

dotenv.load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
API_KEY = os.environ.get('API_KEY')


def pluralize(amount, unit):
    if amount == 0:
        return ''
    elif amount != 1:
        unit += 's'
    return f'{amount:.0f} {unit}'


def format_time(seconds, days=False):
    if days:
        d, s = divmod(seconds, 86400)
        h, s = divmod(s, 3600)
        m, s = divmod(s, 60)
        formatted = {
            'days': pluralize(d, 'day'),
            'hours': pluralize(h, 'hour'),
            'minutes': pluralize(m, 'minute'),
            'seconds': pluralize(s, 'second'),
        }
        if not d and not h:
            result = ', '.join((formatted['minutes'], formatted['seconds']))
        else:
            result = ', '.join(
                (formatted['days'], formatted['hours'], formatted['minutes'])
            )
        return result.strip(' ,')

    h, s = divmod(seconds, 3600)
    m, s = divmod(s, 60)
    return f"{pluralize(h, 'hour')}, {pluralize(m, 'minute')}".strip(' ,')


def get_duration(item_ids):
    """Accept a list of item ids and return their total duration as an int."""
    url = 'https://www.googleapis.com/youtube/v3/videos'

    params = {
        'key': API_KEY,
        'part': ['contentDetails'],
        'id': ','.join(item_ids),
        'fields': 'items/contentDetails/duration',
    }

    r = requests.get(url, params=params)
    items = r.json().get('items')
    if not items:
        return 0
    durations = [
        isodate.parse_duration(i['contentDetails']['duration']).total_seconds()
        for i in items
    ]
    return int(sum(durations))


def get_playlist_meta(playlist_id):
    url = 'https://www.googleapis.com/youtube/v3/playlists'
    params = {
        'key': API_KEY,
        'part': ['snippet', 'contentDetails'],
        'id': playlist_id,
        'fields': 'items(snippet(title,channelTitle),contentDetails/itemCount)',
    }
    r = requests.get(url, params=params)
    data = r.json().get('items')[0]
    return {
        'channel_title': data['snippet']['channelTitle'],
        'playlist_title': data['snippet']['title'],
        'item_count': data['contentDetails']['itemCount'],
    }


def get_result(playlist_id):
    """Calculate playlist duration.

    Return playlist/album duration as a formatted string based on a valid id
    and selected meta data about the playlist.
    In case of an invalid id return an API error message or an empty string.
    """
    url = 'https://www.googleapis.com/youtube/v3/playlistItems'
    params = {
        'key': API_KEY,
        'part': ['snippet'],
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

    playlist_meta = get_playlist_meta(playlist_id)  # extra call

    return {
        'duration': format_time(total_duration, days=True),
        'playlist_title': playlist_meta.get('playlist_title'),
        'channel_title': playlist_meta.get('channel_title'),
        'item_count': playlist_meta.get('item_count'),
    }
