from mapy.context_processors import *


def test_get_country_from_ip_invalid_ip():
    """
    Can't access the database, so we test, if the function returns None for an invalid IP.
    """
    header_line = "Received: from mail.example.com (client.example.com [invalid_ip])"
    expected_result = None

    result = get_country_from_ip(header_line)
    assert result == expected_result


def test_duration_basic():
    seconds = 3665
    expected_result = '1 hr, 1 min, 5 sec'

    result = duration(seconds)
    assert result == expected_result


def test_duration_with_weeks():
    seconds = 604800 + 86400 + 3600 + 60 + 1  # 1 week, 1 day, 1 hour, 1 minute, 1 second
    expected_result = '1 wk, 1 d, 1 hr, 1 min, 1 sec'

    result = duration(seconds)
    assert result == expected_result
