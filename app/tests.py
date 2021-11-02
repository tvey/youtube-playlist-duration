import pytest

from utils import (
    format_time,
)


@pytest.mark.parametrize(
    "seconds,result",
    [
        (60, '1 minute'),
        (3600, '1 hour'),
        (86400, '1 day'),
        (10, '10 seconds'),
        (12345, '3 hours, 25 minutes'),
        (176400, '2 days, 1 hour'),
        (1381, '23 minutes, 1 second'),
        (90000, '1 day, 1 hour'),
        (0, ''),
    ],
)
def test_format_time_with_valid_params(seconds, result):
    assert format_time(seconds) == result


@pytest.mark.parametrize('value', [12345.0, '3600', 'twenty', 0.2])
def test_format_time_with_invalid_input(value):
    with pytest.raises(TypeError, match='must be int'):
        format_time(value)
