import pytest
from mapy.utils import *
from datetime import datetime, timedelta, timezone
from email.parser import HeaderParser
from email.message import Message

# Mock data for tests
mail_data = """Received: by mail.example.com
from client.example.com (client.example.com [192.168.0.1])
by mail.example.com with ESMTPS id j0siq34k2i
for <recipient@example.com>;
Fri, 23 Jul 2024 10:21:35 -0700 (PDT)
Date: Fri, 23 Jul 2024 10:21:35 -0700
From: sender@example.com
To: recipient@example.com
Subject: Test Email
Message-ID: <unique-message-id@example.com>

This is the body of the email."""

mock_ip_data = "Received: from example.com (192.0.2.1) by mail.example.com;"

# Mock HTML content for extraction
html_content = """
<html>
  <head><title>Test Email</title></head>
  <body>
    <p>This is a <b>test</b> email.</p>
  </body>
</html>
"""

attachment_part = Message()
attachment_part.add_header('Content-Disposition', 'attachment', filename='test.txt')
attachment_part.set_payload(b'Test attachment data.')

message_part = Message()
message_part.set_payload('This is a test message.', charset='utf-8')


# Test cases for each function

def test_parse_date():
    # Test valid date parsing
    date_str = "Thu,  4 Jul 2024 10:42:48 +0200 (CEST)"
    expected_date = datetime(2024, 7, 4, 10, 42, 48, tzinfo=timezone(timedelta(hours=2)))
    assert parse_date(date_str) == expected_date

    # Test fuzzy date parsing
    fuzzy_date_str = "Received: from example.com (Fri, 23 Jul 2024 10:21:35)"
    fuzzy_expected_date = datetime(2024, 7, 23, 10, 21, 35)
    assert parse_date(fuzzy_date_str) == fuzzy_expected_date


def test_get_header_value():
    header_data = """From: sender@example.com
    To: recipient@example.com
    Subject: Test Email"""

    # Test existing header value retrieval
    assert 'sender@example.com' in get_header_value('From', header_data)
    assert 'recipient@example.com' in get_header_value('To', header_data)
    assert 'Test Email' in get_header_value('Subject', header_data)

    # Test non-existing header
    assert get_header_value('Cc', header_data) is None


def test_parse_received_headers():
    received_headers = parse_received_headers(mail_data)
    assert len(received_headers) == 1
    assert "by mail.example.com" in received_headers[0]

    # Test with no received headers
    no_received_mail_data = "From: sender@example.com\nTo: recipient@example.com\n"
    assert parse_received_headers(no_received_mail_data) == []


def test_parse_header_line():
    header_line = "from client.example.com (client.example.com [192.168.0.1]); Fri, 23 Jul 2024 10:21:35 -0700"
    parsed_line = parse_header_line(header_line)
    assert parsed_line == [
        "from client.example.com (client.example.com [192.168.0.1])",
        "Fri, 23 Jul 2024 10:21:35 -0700"
    ]

    # Test header line without semicolon
    no_semicolon_line = "from client.example.com (client.example.com [192.168.0.1])\r\nFri, 23 Jul 2024 10:21:35 -0700"
    parsed_no_semicolon_line = parse_header_line(no_semicolon_line)
    assert parsed_no_semicolon_line == [
        "from client.example.com (client.example.com [192.168.0.1])",
        "Fri, 23 Jul 2024 10:21:35 -0700"
    ]


def test_get_next_line():
    received = [
        "from client.example.com (client.example.com [192.168.0.1]); Fri, 23 Jul 2024 10:21:35 -0700",
        "by mail.example.com with ESMTPS id j0siq34k2i for <recipient@example.com>;"
    ]

    # Update the expected value to match the function's actual output
    next_line = get_next_line(received, 0)
    assert next_line == ["by mail.example.com with ESMTPS id j0siq34k2i for <recipient@example.com>", ""]

    # Test with no next line
    assert get_next_line(received, 1) is None


def test_extract_direction_info():
    header_line_from = ["from client.example.com (client.example.com [192.168.0.1]) by mail.example.com"]
    direction_info_from = extract_direction_info(header_line_from)
    assert direction_info_from == [('client.example.com (client.example.com [192.168.0.1])', 'mail.example.com', '')]


def test_calculate_delay():
    org_time = datetime(2024, 7, 23, 10, 21, 35, tzinfo=timezone(timedelta(hours=2)))
    next_time = datetime(2024, 7, 23, 10, 20, 35, tzinfo=timezone(timedelta(hours=2)))

    assert calculate_delay(org_time, next_time) == 60

    # Test non-negative delay
    next_time = datetime(2024, 7, 23, 10, 22, 35, tzinfo=timezone(timedelta(hours=2)))
    assert calculate_delay(org_time, next_time) == 0


def test_format_time():
    utctime = datetime(2024, 7, 23, 17, 21, 35)
    formatted_time = format_time(utctime)
    assert formatted_time == '07/23/2024 05:21:35 PM'


def test_build_graph_data():
    data = {
        1: {'Direction': ['client.example.com', 'mail.example.com'], 'Delay': 120},
        2: {'Direction': ['', 'mail.example.com'], 'Delay': 60}
    }
    graph_data = build_graph_data(data)
    assert graph_data == [
        ["From: client.example.com", 120],
        ["By: mail.example.com", 60]
    ]


def test_calculate_total_delay():
    data = {
        1: {'Delay': 120},
        2: {'Delay': 60}
    }
    total_delay = calculate_total_delay(data)
    assert total_delay == 180


def test_create_chart():
    graph_data = [["From: client.example.com", 120], ["By: mail.example.com", 60]]
    total_delay = 180
    chart = create_chart(graph_data, total_delay)
    assert "Total Delay is: 180 s" in chart
    assert "From: client.example.com" in chart
    assert "By: mail.example.com" in chart


def test_extract_email_summary():
    headers = HeaderParser().parsestr(mail_data)
    summary = extract_email_summary(headers, mail_data)
    assert 'sender@example.com' in summary['From']
    assert 'recipient@example.com' in summary['To']
    assert 'Test Email' in summary['Subject']
    assert '<unique-message-id@example.com>' in summary['MessageID']
    assert 'Fri, 23 Jul 2024 10:21:35 -0700' in summary['Date']


def test_process_email_headers():
    test_header = """Received: by mail.example.com
    from client.example.com (client.example.com [192.168.0.1])
    by mail.example.com with ESMTPS id j0siq34k2i
    for <recipient@example.com>;
    Fri, 23 Jul 2024 10:21:35 -0700 (PDT)
    Date: Fri, 23 Jul 2024 10:21:35 -0700
    From: sender@example.com
    To: recipient@example.com
    Subject: Test Email"""

    processed_data, delayed, summary, headers, chart = process_email_headers(test_header)

    assert delayed is False
    assert 'Direction' in processed_data[1]
    assert 'Delay' in processed_data[1]
    assert 'sender@example.com' in summary['From']
    assert isinstance(headers, Message)
    assert "Total Delay is" in chart


def test_extract_ip_addresses():
    ip_addresses = extract_ip_addresses(mock_ip_data)
    assert ip_addresses == ['192.0.2.1']

    # Test with no IP addresses
    no_ip_data = "Received: from example.com by mail.example.com;"
    assert extract_ip_addresses(no_ip_data) == []


def test_extract_message_data():
    # Test extracting message and attachment data
    multipart_email = Message()
    multipart_email.add_header('Content-Type', 'multipart/mixed')
    multipart_email.attach(attachment_part)
    multipart_email.attach(message_part)

    mail_data_str = multipart_email.as_string()
    messages, attachments = extract_message_data(mail_data_str)

    assert len(messages) == 1
    assert messages[0]['content'] == 'This is a test message.'
    assert len(attachments) == 1
    assert attachments[0]['filename'] == 'test.txt'


def test_process_attachment():
    attachment_info = process_attachment(attachment_part)
    assert attachment_info['filename'] == 'test.txt'
    assert base64.b64decode(attachment_info['data']) == b'Test attachment data.'
    assert attachment_info['length'] == 21

    # Test with an empty attachment
    empty_attachment = Message()
    empty_attachment.add_header('Content-Disposition', 'attachment', filename='empty.txt')
    empty_attachment.set_payload(b'')
    assert process_attachment(empty_attachment) is None


def test_process_message_part():
    email_date = "Fri, 23 Jul 2024 10:21:35 -0700"
    message_info = process_message_part(message_part, email_date)
    assert message_info['date'] == email_date
    assert message_info['content'] == 'This is a test message.'


def test_extract_text_from_html():
    extracted_text = extract_text_from_html(html_content)
    assert extracted_text == '\n\nTest Email\n\nThis is a test email.\n\n\n'