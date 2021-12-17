import asyncio
import os
from typing import Union

import isodate
from aiohttp_client_cache import CachedSession, SQLiteBackend


API_KEY = os.environ.get('API_KEY')
BASE_URL = 'https://www.googleapis.com/youtube/v3/'


def pluralize(amount: Union[int, float], unit: str) -> str:
    amount = int(amount)
    if amount == 0:
        return ''
    elif amount > 1:
        unit += 's'
    return f'{amount:.0f} {unit}'


def format_time(seconds: Union[int, float]) -> str:
    try:
        seconds = int(seconds)
    except ValueError:
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
    return result.strip(' ,')


def calc_total_hours(seconds: Union[int, float]) -> int:
    h, _ = divmod(int(seconds), 3600)
    return h


async def get_duration(session: CachedSession, item_ids: list):
    """Accept a list of at most 50 item ids and return their total duration."""
    params = {
        'key': API_KEY,
        'part': ['contentDetails'],
        'id': ','.join(item_ids),
        'fields': 'items/contentDetails/duration',
    }

    async with session.get(f'{BASE_URL}videos', params=params) as r:
        data = await r.json()
        items = data.get('items')
        if not items:
            return 0
        durations = [
            isodate.parse_duration(
                i['contentDetails']['duration']
            ).total_seconds()
            for i in items
        ]
        return int(sum(durations))


async def get_playlist_meta(session: CachedSession, playlist_id: str) -> dict:
    """Fetch extra data about a playlist.

    The meta data includes:
        * channel title / playlist creator / artist for music albums
        * playlist title / album name
        * items (count and type)

    Need to make extra calls, as neither resource (playlists/playlistItems)
    returns all the fields wanted for music albums.
    """
    params = {
        'key': API_KEY,
        'part': ['snippet', 'contentDetails'],
        'id': playlist_id,
        'fields': 'items(snippet(title,channelTitle),contentDetails/itemCount)',
    }
    async with session.get(f'{BASE_URL}playlists', params=params) as r:
        data = await r.json()
        playlist = data.get('items')[0]
        item_count = playlist['contentDetails']['itemCount']

    result = {
        'channel_title': playlist['snippet']['channelTitle'],
        'playlist_title': playlist['snippet']['title'],
        'item_count': item_count,
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
        async with session.get(f'{BASE_URL}playlistItems', params=params) as r:
            data = await r.json()
            artist = data.get('items')[0]['snippet']['videoOwnerChannelTitle']
            result['channel_title'] = artist.split(' - Topic')[0]

    if playlist_id.startswith('OLAK5uy'):
        result['items'] = pluralize(item_count, 'song')
    else:
        result['items'] = pluralize(item_count, 'item')
    return result


async def get_result(playlist_id):
    """Calculate playlist duration.

    Return playlist/album duration as a formatted string based on a valid id
    and some meta data about the playlist.
    In case of an invalid id return an API error message and code.
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

    async with CachedSession(cache=SQLiteBackend('youtube')) as session:
        tasks = []
        while True:
            async with session.get(url, params=params) as r:
                data = await r.json()

            if not data.get('items'):
                if data.get('error'):
                    return {
                        'error': data.get('error').get('message'),
                        'code': data.get('error').get('code'),
                    }
                else:
                    return {}
            item_ids = [
                v['snippet']['resourceId']['videoId'] for v in data['items']
            ]
            tasks.append(asyncio.create_task(get_duration(session, item_ids)))

            next_page_token = data.get('nextPageToken')

            if not next_page_token:
                break
            params['pageToken'] = next_page_token

        duration_results = await asyncio.gather(*tasks)
        total_duration = sum(duration_results)
        playlist_meta = await get_playlist_meta(session, playlist_id)

    item_count = playlist_meta['item_count']
    formatted_duration = format_time(total_duration)
    print(f'Total duration for {playlist_id}: {format_time(total_duration)}')
    total_hours = None
    if 'day' in formatted_duration:
        total_hours = calc_total_hours(total_duration)

    return {
        'duration': formatted_duration,
        'total_hours': total_hours,
        'playlist_title': playlist_meta.get('playlist_title'),
        'channel_title': playlist_meta.get('channel_title'),
        'items': playlist_meta.get('items'),
        'avg_duration': format_time(total_duration / item_count),
        'speed_1.25': format_time(total_duration / 1.25),
        'speed_1.5': format_time(total_duration / 1.5),
        'speed_1.75': format_time(total_duration / 1.75),
        'speed_2': format_time(total_duration / 2),
    }
