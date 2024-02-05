import pytest
from aiohttp_client_cache import CachedSession, SQLiteBackend

from app.utils import (
    format_time,
    pluralize,
    calc_total_hours,
    get_duration,
    get_playlist_meta,
    get_result,
)


@pytest.mark.parametrize(
    'value,unit,result',
    [
        (21, 'second', '21 seconds'),
        (12, 'cucumber', '12 cucumbers'),
        (1, 'hour', '1 hour'),
        (0, 'year', ''),
        (0, 'minute', ''),
    ],
)
def test_pluralize(value, unit, result):
    assert pluralize(value, unit) == result


@pytest.mark.parametrize(
    'seconds,result',
    [
        (60, '1 minute'),
        (3600, '1 hour'),
        (86400, '1 day'),
        (10, '10 seconds'),
        (12345, '3 hours, 25 minutes'),
        (176400, '2 days, 1 hour'),
        (1381, '23 minutes, 1 second'),
        (90000, '1 day, 1 hour'),
        (0, '0 minutes'),
    ],
)
def test_format_time_with_valid_params(seconds, result):
    print(format_time(seconds))
    assert format_time(seconds) == result


@pytest.mark.parametrize(
    'value', 
    ['3600.0', 'twenty', -123]
)
def test_format_time_with_invalid_input(value):
    with pytest.raises((TypeError, ValueError)):
        format_time(value)


@pytest.mark.parametrize(
    'value,unit',
    [
        ('42', 42),
        ('eleven', 'hour'),
        (11, 11),
        (None, None),
    ],
)
def test_pluralize_with_invalid_input(value, unit):
    with pytest.raises((ValueError, TypeError)):
        pluralize(value, unit)


@pytest.mark.parametrize(
    'value,result',
    [
        (30, 0),
        (3600, 1),
        (123456, 34),
        ('8000', 2),
    ],
)
def test_calc_total_hours(value, result):
    assert calc_total_hours(value) == result


@pytest.mark.parametrize('value', ['', 'five thousand'])
def test_calc_total_hours_with_invalid_input(value):
    with pytest.raises((ValueError)):
        calc_total_hours(value)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'video_ids,result',
    [
        ([''], 0),
        (['dQw4w9WgXcQ'], 213),
        (['rP0uuI80wuY', 'rVeMiVU77wo'], 491),
        (['Tt5lB-RoAi4', 'mkUZFV8g0YE', 'BBiczdCEBMM'], 386),
        (['vRBihr41JTo', 'E87JdbqStx8', 'eLsxXkjqipg', 'w6T02g5hnT4'], 1364),
    ],
)
async def test_get_duration(video_ids, result):
    async with CachedSession(cache=SQLiteBackend('youtube')) as session:
        duration = await get_duration(session, video_ids)
        assert isinstance(duration, int)
        assert duration == result


@pytest.mark.asyncio
async def test_get_playlist_meta(playlist_id_fix):
    async with CachedSession(cache=SQLiteBackend('youtube')) as session:
        result = await get_playlist_meta(session, playlist_id_fix)
        assert result.get('channel_title')
        assert result.get('playlist_title')
        assert result.get('item_count')
        items = result.get('items')
        assert items
        assert 'video' in items or 'song' in items


@pytest.mark.asyncio
async def test_get_playlist_meta_with_invalid_id(invalid_playlist_id_fix):
    result = await get_result(invalid_playlist_id_fix)
    assert result.get('error')


@pytest.mark.asyncio
async def test_get_playlist_meta_with_no_id():
    result = await get_result('')
    assert result.get('error')


@pytest.mark.asyncio
async def test_get_result(playlist_id_fix):
    result = await get_result(playlist_id_fix)
    assert result.get('duration')
    assert result.get('playlist_title')
    assert result.get('channel_title')
    assert result.get('items')


@pytest.mark.asyncio
async def test_get_result_with_invalid_id(invalid_playlist_id_fix):
    result = await get_result(invalid_playlist_id_fix)
    assert result.get('error')


@pytest.mark.asyncio
async def test_get_result_with_no_id():
    result = await get_result('')
    assert result.get('error')


@pytest.mark.asyncio
async def test_result_on_id_list(playlist_id_list):
    for playlist_id in playlist_id_list(size=10):
        print(playlist_id)
        result = await get_result(playlist_id)
        if result.get('error'):
            print(f'{result.get("code")} {result.get("error")}')
        else:
            playlist, channel = result['playlist_title'], result['channel_title']
            print(f'{playlist} ({channel}), {result["duration"]}')
        assert result
