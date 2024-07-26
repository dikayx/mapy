import re
from IPy import IP
import geoip2.database
import os

# Define path to GeoLite2-Country.mmdb
mmdb_path = os.path.join(os.path.dirname(__file__), 'static', 'data', 'GeoLite2-Country.mmdb')

# Initialize the GeoIP2 reader
reader = geoip2.database.Reader(mmdb_path)

def get_country_from_ip(line):
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

def duration(seconds, _maxweeks=99999999999):
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
    @app.context_processor
    def utility_processor():
        return dict(
            country=get_country_from_ip,
            duration=duration
        )
