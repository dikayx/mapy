import re
import time
import pygal
import dateutil.parser
from datetime import datetime
from pygal.style import Style
from email.parser import HeaderParser


def date_parser(line: str) -> datetime:
    """
    This function takes a line of text from the email header and tries
    to parse the date from it.

    :param line: A line of text from the email header

    :return: A datetime object
    """
    try:
        # Attempt to parse date using dateutil with fuzzy parsing
        r = dateutil.parser.parse(line, fuzzy=True)

    except ValueError:
        # Handle potential ValueError from incorrect timezones
        r = re.findall(r'^(.*?)\s*(?:\(|utc)', line, re.I)
        if r:
            r = dateutil.parser.parse(r[0])
    return r


def get_header_value(h: str, data: str, rex: str = r'\s*(.*?)\n\S+:\s') -> str:
    """
    This function takes a header name and the email header data and
    returns the value of the header.

    :param h: The header name

    :param data: The email header data
    """
    # Use regular expressions to find header values
    r = re.findall('%s:%s' % (h, rex), data, re.X | re.DOTALL | re.I)
    if r:
        return r[0].strip()
    else:
        return None


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
    delay = (org_time - next_time).seconds
    return max(delay, 0)  # Ensure delay is non-negative


def format_time(utctime: datetime) -> str:
    """
    Format the UTC time to a readable string.

    :param utctime: UTC datetime object

    :return: Formatted time string
    """
    ftime = utctime.utctimetuple()
    return time.strftime('%m/%d/%Y %I:%M:%S %p', ftime)


def build_graph_data(r: dict) -> list:
    """
    Build graph data from parsed header information.

    :param r: Parsed header information

    :return: Graph data for visualization
    """
    graph = []
    for i in list(r.values()):
        if i['Direction'][0]:
            graph.append(["From: %s" % i['Direction'][0], i['Delay']])
        else:
            graph.append(["By: %s" % i['Direction'][1], i['Delay']])
    return graph


def calculate_total_delay(r: dict) -> int:
    """
    Calculate the total delay from all header data.

    :param r: Parsed header information

    :return: Total delay in seconds
    """
    return sum([x['Delay'] for x in list(r.values())])


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
        font_family='googlefont:Open Sans',
    )
    line_chart = pygal.HorizontalBar(
        style=custom_style, height=250, legend_at_bottom=True,
        tooltip_border_radius=10)
    line_chart.tooltip_fancy_mode = False
    line_chart.title = 'Total Delay is: %s' % total_delay
    line_chart.x_title = 'Delay in seconds.'
    for i in graph:
        line_chart.add(i[0], i[1])
    return line_chart.render(is_unicode=True)


def extract_email_summary(n: HeaderParser, mail_data: str) -> dict:
    """
    Extract email summary information.

    :param n: Parsed email headers
    :param mail_data: Raw email data

    :return: Email summary information as a dictionary
    """
    return {
        'From': n.get('From') or get_header_value('from', mail_data),
        'To': n.get('to') or get_header_value('to', mail_data),
        'Cc': n.get('cc') or get_header_value('cc', mail_data),
        'Subject': n.get('Subject') or get_header_value('Subject', mail_data),
        'MessageID': n.get('Message-ID') or get_header_value('Message-ID', mail_data),
        'Date': n.get('Date') or get_header_value('Date', mail_data),
    }


def process_email_headers(mail_data: str):
    """
    Process email headers and generate graph data.

    :param mail_data: Raw email data

    :return: Processed data, delay status, email summary, parsed headers, and chart
    """
    received = parse_received_headers(mail_data)
    n = HeaderParser().parsestr(mail_data)
    r = {}
    c = len(received)

    for i in range(len(received)):
        line = parse_header_line(received[i])
        next_line = get_next_line(received, i)

        org_time = date_parser(line[-1])
        next_time = date_parser(next_line[-1]) if next_line else org_time

        data = extract_direction_info(line)
        delay = calculate_delay(org_time, next_time)

        try:
            ftime = format_time(org_time)
            r[c] = {
                'Timestmp': org_time,
                'Time': ftime,
                'Delay': delay,
                'Direction': [x.replace('\n', ' ') for x in list(map(str.strip, data[0]))]
            }
            c -= 1
        except IndexError:
            pass

    graph = build_graph_data(r)
    total_delay = calculate_total_delay(r)
    delayed = bool(total_delay)
    chart = create_chart(graph, total_delay)

    summary = extract_email_summary(n, mail_data)

    return r, delayed, summary, n, chart
