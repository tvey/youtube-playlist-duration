import os
import re

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

        if s > 30:
            m += 1
        return

    h, s = divmod(seconds, 3600)
    m, s = divmod(s, 60)
    return f'{h:02.0f}:{m:02.0f}:{s:02.0f}'  # format for now


def format_result():
    pass


def calculate_duration(data) -> float:
    durations = [
        isodate.parse_duration(i['contentDetails']['duration']).total_seconds()
        for i in data
    ]
    return sum(durations)


def get_video_duration(video_ids):
    """Accept a list of video ids and return their total duration."""
    url = 'https://www.googleapis.com/youtube/v3/videos'

    params = {
        'key': API_KEY,
        'part': ['contentDetails'],
        'id': ','.join(video_ids),
        'fields': 'items/contentDetails/duration',
    }

    r = requests.get(url, params=params)
    items = r.json().get('items')
    return calculate_duration(items)


def get_result(playlist_id):
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
            return ''

        video_ids = [
            v['snippet']['resourceId']['videoId'] for v in data['items']
        ]
        total_duration += get_video_duration(video_ids)
        next_page_token = data.get('nextPageToken')

        if not next_page_token:
            break
        params['pageToken'] = next_page_token

    return format_time(total_duration)
