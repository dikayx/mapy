import re
from IPy import IP
import geoip2.database
import os

mmdb_path = os.path.join(os.path.dirname(__file__), 'static', 'data', 'GeoLite2-Country.mmdb')
reader = geoip2.database.Reader(mmdb_path)


def get_country_from_ip(line) -> dict:
    """
    Get country information from an IP address which is part of a header line.

    :param line: A header line

    :return: Country information as a dictionary like {'iso_code': 'us', 'country_name': 'United States'}
    """
    ipv4_address = re.compile(r"""
        \b((?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)\.
        (?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)\.
        (?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)\.
        (?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d))\b""", re.X)
    ip = ipv4_address.findall(line)
    if ip:
        ip = ip[0]  # Take the 1st IP and ignore the rest
        if IP(ip).iptype() == 'PUBLIC':
            r = reader.country(ip).country
            if r.iso_code and r.name:
                return {
                    'iso_code': r.iso_code.lower(),
                    'country_name': r.name
                }


def duration(seconds, _maxweeks=99999999999) -> str:
    """
    Convert seconds to a human-readable duration.

    :param seconds: The number of seconds
    :param _maxweeks: Just for internal use, don't worry about it

    :return: A human-readable duration string like '1 wk, 2 d, 3 hr, 4 min, 5 sec'
    """
    return ', '.join(
        '%d %s' % (num, unit)
        for num, unit in zip([
            (seconds // d) % m
            for d, m in (
                (604800, _maxweeks),
                (86400, 7), (3600, 24),
                (60, 60), (1, 60))
        ], ['wk', 'd', 'hr', 'min', 'sec'])
        if num
    )


def register_context_processors(app):
    """
    Register context processors which can be directly used in templates. They are registered here
    and not in the 'app.py' like the blueprints because they are not specific to a blueprint.

    :param app: The Flask application instance
    """

    @app.context_processor
    def utility_processor():
        return dict(
            country=get_country_from_ip,
            duration=duration
        )
