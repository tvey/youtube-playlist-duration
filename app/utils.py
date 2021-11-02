import os

import requests
import dotenv
import isodate
import requests_cache

requests_cache.install_cache('youtube')

dotenv.load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
API_KEY = os.environ.get('API_KEY')
BASE_URL = 'https://www.googleapis.com/youtube/v3/'


def pluralize(amount, unit):
    if amount == 0:
        return ''
    elif amount != 1:
        unit += 's'
    return f'{amount:.0f} {unit}'


def format_time(seconds):
    if not isinstance(seconds, int):
        raise TypeError('Duration in seconds must be int.')
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
        if h:
            result = ', '.join(
                (formatted['days'], formatted['hours'], formatted['minutes'])
            )
        else:
            result = ', '.join((formatted['days'], formatted['minutes']))
    print(result)
    return result.strip(' ,')


def get_total_hours(seconds):
    h, s = divmod(seconds, 3600)
    return h


def get_duration(item_ids):
    """Accept a list of item ids and return their total duration as an int."""
    params = {
        'key': API_KEY,
        'part': ['contentDetails'],
        'id': ','.join(item_ids),
        'fields': 'items/contentDetails/duration',
    }

    r = requests.get(f'{BASE_URL}videos', params=params)
    items = r.json().get('items')
    if not items:
        return 0
    durations = [
        isodate.parse_duration(i['contentDetails']['duration']).total_seconds()
        for i in items
    ]
    return int(sum(durations))


def get_playlist_meta(playlist_id):
    params = {
        'key': API_KEY,
        'part': ['snippet', 'contentDetails'],
        'id': playlist_id,
        'fields': 'items(snippet(title,channelTitle),contentDetails/itemCount)',
    }
    r = requests.get(f'{BASE_URL}playlists', params=params)
    data = r.json().get('items')[0]

    result = {
        'channel_title': data['snippet']['channelTitle'],
        'playlist_title': data['snippet']['title'],
        'item_count': data['contentDetails']['itemCount'],
    }

    if playlist_id.startswith('OLAK5uy'):  # music album
        album_title = result['playlist_title'].split('Album - ')[1]
        result['playlist_title'] = album_title
        params = {
            'key': API_KEY,
            'part': ['snippet'],
            'playlistId': playlist_id,
            'fields': 'items/snippet/videoOwnerChannelTitle',
        }
        r = requests.get(f'{BASE_URL}playlistItems', params=params)
        artist = r.json().get('items')[0]['snippet']['videoOwnerChannelTitle']
        result['channel_title'] = artist.split(' - Topic')[0]

    return result


def get_result(playlist_id):
    """Calculate playlist duration.

    Return playlist/album duration as a formatted string based on a valid id
    and some meta data about the playlist.
    In case of an invalid id return an API error message or an empty string.
    """
    url = f'{BASE_URL}playlistItems'
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

    playlist_meta = get_playlist_meta(playlist_id)  # extra calls
    d, s = divmod(total_duration, 86400)
    total_hours = 0
    if d:
        total_hours = get_total_hours(total_duration)

    return {
        'duration': format_time(total_duration),
        'total_hours': total_hours,
        'playlist_title': playlist_meta.get('playlist_title'),
        'channel_title': playlist_meta.get('channel_title'),
        'item_count': playlist_meta.get('item_count'),
    }
