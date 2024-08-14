# Certain parts of this code are adapted from CyberDefenders' MHA project.
# Original source: https://github.com/cyberdefenders/MHA

import base64
import re
import time

from datetime import datetime
from email.parser import HeaderParser
from email import message_from_string
from email.message import Message
from email.utils import parseaddr

import dateutil.parser
import pygal
import requests

from bs4 import BeautifulSoup
from pygal.style import Style
from typing import Optional


def try_parse_date(date_str: str) -> datetime:
    """
    Attempts to parse a date string using dateutil parser with fuzzy parsing.

    :param date_str: A date string to parse

    :return: A datetime object or None if parsing fails
    """
    try:
        return dateutil.parser.parse(date_str, fuzzy=True)
    except ValueError:
        return None


def extract_and_parse_date(line: str, regex: str) -> datetime:
    """
    Extracts date string from a line using a regex pattern and attempts to parse it.

    :param line: A line of text from the email header
    :param regex: A regex pattern to extract the date string

    :return: A datetime object or None if parsing fails
    """
    match = re.findall(regex, line, re.I)
    if match:
        # If match is a tuple (from multiple groups), use the first group
        date_str = match[0] if isinstance(match[0], str) else match[0][0]
        return try_parse_date(date_str)
    return None


def parse_date(line: str) -> datetime:
    """
    Parses the date from a line of text from the email header.

    :param line: A line of text from the email header

    :return: A datetime object
    """
    result = try_parse_date(line)
    
    # Try manually if fuzzy parsing fails
    if result is None:
        result = extract_and_parse_date(line, r'^(.*?)\s*(?:\(|utc)')
    
    # Handle the most exotic cases of date formats
    if result is None:
        result = extract_and_parse_date(line, r'(?P<date>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)? \+\d{4}|(?P<weekday>[a-zA-Z]{3}), \d{2} [a-zA-Z]{3} \d{4} \d{2}:\d{2}:\d{2}(?:\.\d+)? \+\d{4})')
    
    return result


def get_header_value(h: str, data: str, rex: str = r'\s*(.*?)(?:\n\S+:|$)') -> str | None:
    """
    This function takes a header name and the email header data and
    returns the value of the header. For 'from', 'to', or 'cc' headers,
    it validates if the value is a valid email address.

    :param h: The header name
    :param data: The email header data
    :param rex: The regular expression pattern for matching the header value

    :return: The value of the header or None if not found or invalid email
    """
    matches = re.findall(f'{h}:{rex}', data, re.X | re.DOTALL | re.I)
    
    if not matches:
        return None
    
    header_value = matches[0].strip()
    
    if h.lower() not in {'from', 'to', 'cc'}:
        return header_value

    _, email = parseaddr(header_value)
    
    return header_value if re.match(r'^[^@]+@[^@]+\.[^@]+$', email) else None


def parse_received_headers(mail_data: str) -> list:
    """
    Parse the Received headers from email data.

    :param mail_data: Raw email data containing headers

    :return: A list of Received headers
    """
    n = HeaderParser().parsestr(mail_data)
    received = n.get_all('Received')
    if received:
        # Filter headers containing 'from' or 'by'
        received = [i for i in received if ('from' in i or 'by' in i)]
    else:
        # Regex to find 'Received' headers in raw mail data
        received = re.findall(
            r'Received:\s*(.*?)\n\S+:\s+', mail_data, re.X | re.DOTALL | re.I
        )
    return received


def parse_header_line(header_line: str) -> list:
    """
    Parse a single Received header line.

    :param header_line: A single Received header line

    :return: A list of parts of the header line
    """
    if ';' in header_line:
        line = header_line.split(';')
    else:
        line = header_line.split('\r\n')
    line = list(map(str.strip, line))
    line = [x.replace('\r\n', ' ') for x in line]
    return line


def get_next_line(received: list, index: int) -> list:
    """
    Get the next line of Received headers, if available.

    :param received: List of Received headers
    :param index: Current index

    :return: Next line of Received headers
    """
    try:
        if ';' in received[index + 1]:
            next_line = received[index + 1].split(';')
        else:
            next_line = received[index + 1].split('\r\n')
        next_line = list(map(str.strip, next_line))
        next_line = [x.replace('\r\n', '') for x in next_line]
    except IndexError:
        next_line = None
    return next_line


def extract_direction_info(line: list) -> list:
    """
    Extract direction information from a header line.

    :param line: A list of parts of the header line

    :return: Extracted direction information
    """
    if line[0].startswith('from'):
        data = re.findall(
            r"""
            from\s+
            (.*?)\s+
            by\s+(.*?)
            (?:
                (?:with|via)
                (.*?)
                (?:\sid\s|$)
                |\sid\s|$
            )""", line[0], re.DOTALL | re.X)
    else:
        data = re.findall(
            r"""
            ()by
            (.*?)
            (?:
                (?:with|via)
                (.*?)
                (?:\sid\s|$)
                |\sid\s
            )""", line[0], re.DOTALL | re.X)
    return data


def calculate_delay(org_time: datetime, next_time: datetime) -> int:
    """
    Calculate the delay between two timestamps.

    :param org_time: Original timestamp
    :param next_time: Next timestamp

    :return: Delay in seconds (non-negative)
    """
    delay = (org_time - next_time).total_seconds()
    return max(int(delay), 0)  # Ensure delay is non-negative


def format_time(utctime: datetime) -> str:
    """
    Format the UTC time to a readable string.

    :param utctime: UTC datetime object

    :return: Formatted time string
    """
    ftime = utctime.utctimetuple()
    return time.strftime('%m/%d/%Y %I:%M:%S %p', ftime)


def build_graph_data(data: dict) -> list:
    """
    Build graph data from parsed header information.

    :param data: Parsed header information

    :return: Graph data for visualization
    """
    graph = []
    for i in list(data.values()):
        if i['Direction'][0]:
            graph.append(["From: %s" % i['Direction'][0], i['Delay']])
        else:
            graph.append(["By: %s" % i['Direction'][1], i['Delay']])
    return graph


def calculate_total_delay(data: dict) -> int:
    """
    Calculate the total delay from all header data.

    :param data: Parsed header information

    :return: Total delay in seconds
    """
    return sum([x['Delay'] for x in list(data.values())])


def create_chart(graph: list, total_delay: int) -> str:
    """
    Create a Pygal chart from graph data.

    :param graph: Graph data for visualization
    :param total_delay: Total delay to display on the chart

    :return: Rendered chart as a unicode string
    """
    custom_style = Style(
        background='transparent',
        plot_background='transparent',
        font_family='system-ui',
    )
    line_chart = pygal.HorizontalBar(
        style=custom_style, height=250, legend_at_bottom=True,
        tooltip_border_radius=10)
    line_chart.tooltip_fancy_mode = False
    line_chart.title = 'Total Delay is: %s s' % total_delay
    line_chart.x_title = 'Delay in seconds.'
    for i in graph:
        line_chart.add(i[0], i[1])
    return line_chart.render(is_unicode=True)


def extract_email_summary(headers: HeaderParser, mail_data: str) -> dict:
    """
    Extract email summary information from either parsed headers or raw email data.

    :param headers: Parsed email headers
    :param mail_data: Raw email data

    :return: Email summary information as a dictionary
    """
    return {
        'From': headers.get('From') or get_header_value('from', mail_data),
        'To': headers.get('to') or get_header_value('to', mail_data),
        'Cc': headers.get('cc') or get_header_value('cc', mail_data),
        'Subject': headers.get('Subject') or get_header_value('Subject', mail_data),
        'MessageID': headers.get('Message-ID') or get_header_value('Message-ID', mail_data),
        'Date': headers.get('Date') or get_header_value('Date', mail_data),
    }


def process_email_headers(mail_data: str) -> tuple:
    """
    Process email headers and generate graph data.

    :param mail_data: Raw email data

    :return: Processed data, delay status, email summary, parsed headers, and chart
    """
    received = parse_received_headers(mail_data)
    headers = HeaderParser().parsestr(mail_data)
    data = {}
    c = len(received)

    for i in range(len(received)):
        line = parse_header_line(received[i])
        next_line = get_next_line(received, i)

        org_time = parse_date(line[-1])
        next_time = parse_date(next_line[-1]) if next_line else org_time

        direction_info = extract_direction_info(line)
        delay = calculate_delay(org_time, next_time)

        try:
            ftime = format_time(org_time)
            data[c] = {
                'Timestamp': org_time,
                'Time': ftime,
                'Delay': delay,
                'Direction': [x.replace('\n', ' ') for x in list(map(str.strip, direction_info[0]))]
            }
            c -= 1
        except IndexError:
            pass

    graph = build_graph_data(data)
    total_delay = calculate_total_delay(data)
    delayed = bool(total_delay)
    chart = create_chart(graph, total_delay)

    summary = extract_email_summary(headers, mail_data)

    return data, delayed, summary, headers, chart


# --- Estimate Geolocation from IP Address --- #

def extract_ip_addresses(mail_data: str) -> list:
    """
    Extract IP addresses from the mail data string.

    :param mail_data: The raw mail data containing headers

    :return: A list of IP addresses found in the mail data
    """
    ip_regex = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'  # IPv4
    ipv6_regex = r'\b(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}\b'  # IPv6

    ipv4_matches = re.findall(ip_regex, mail_data)
    ipv6_matches = re.findall(ipv6_regex, mail_data)

    # Combine and return unique IP addresses
    return list(set(ipv4_matches + ipv6_matches))


def fetch_geolocation(ip: str) -> dict | None:
    """
    Fetch geolocation data for a given IP address.

    :param ip: The IP address

    :return: A dictionary containing latitude, longitude, and IP address
    """
    try:
        response = requests.get(f'https://ipapi.co/{ip}/json/')
        data = response.json()
        if 'latitude' in data and 'longitude' in data:
            return {
                'ip': ip,
                'latitude': data['latitude'],
                'longitude': data['longitude']
            }
    except requests.RequestException as e:
        print(f"Error fetching geolocation for IP {ip}: {e}")

    return None


def extract_ip_geolocations(mail_data: str) -> list:
    """
    Extract IP addresses from mail data and fetch their geolocations.

    :param mail_data: The raw mail data containing headers

    :return: A list of dictionaries with IP, latitude, and longitude
    """
    ip_addresses = extract_ip_addresses(mail_data)
    geolocations = []

    for ip in ip_addresses:
        location = fetch_geolocation(ip)
        if location:
            geolocations.append(location)

    return geolocations


# --- Extract message and attachment data --- #

def extract_message_data(mail_data: str) -> tuple:
    """
    Extract and decode message data from email content, including attachment names and paths.

    :param mail_data: Raw email data

    :return: A tuple containing a list of message data and attachment info (filename and file path)
    """
    msg = message_from_string(mail_data)
    messages = []
    attachments = []

    email_date = msg.get('Date', 'No Date Provided')

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_disposition and 'attachment' in content_disposition:
                attachment_info = process_attachment(part)
                if attachment_info:
                    attachments.append(attachment_info)

            elif content_type in ['text/plain', 'text/html']:
                message_info = process_message_part(part, email_date)
                if message_info:
                    messages.append(message_info)

    else:
        message_info = process_message_part(msg, email_date)
        if message_info:
            messages.append(message_info)

    return messages, attachments


def process_attachment(part: Message) -> Optional[dict]:
    """
    Process an email part as an attachment and return attachment information.

    :param part: The email part representing the attachment

    :return: A dictionary containing the attachment's filename, base64 encoded data, and length
    """
    filename = part.get_filename()
    if not filename:
        return None

    attachment_data = part.get_payload(decode=True)

    encoded_data = base64.b64encode(attachment_data).decode('utf-8')
    return {
        'filename': filename,
        'data': encoded_data,
        'length': len(attachment_data)
    }


def process_message_part(part: Message, email_date: str) -> Optional[dict]:
    """
    Process an email part and return the message content.

    :param part: The email part to process
    :param email_date: The date of the email

    :return: A dictionary containing the date and clean message content
    """
    payload = part.get_payload(decode=True)
    charset = part.get_content_charset() or 'utf-8'

    try:
        decoded_payload = payload.decode(charset, errors='replace')
        clean_text = extract_text_from_html(decoded_payload)

        return {
            'date': email_date,
            'content': clean_text
        }
    except Exception as e:
        return {
            'date': email_date,
            'content': f"Error decoding message: {e}"
        }


def extract_text_from_html(html_content: str) -> str:
    """
    Extract and clean text from HTML content.

    :param html_content: HTML content to clean

    :return: Extracted plain text
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()
