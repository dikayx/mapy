from flask import Blueprint, render_template, request
from mapy.utils import process_email_headers, extract_ip_geolocations, extract_message_data

blueprint = Blueprint('mapy', __name__)


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        mail_data = request.form['headers'].strip()
        data, delayed, summary, headers, chart = process_email_headers(mail_data)
        locations = extract_ip_geolocations(mail_data)
        messages, attachments = extract_message_data(mail_data)  # Extract message data

        security_headers = [
            'Received-SPF', 'Authentication-Results',
            'DKIM-Signature', 'ARC-Authentication-Results'
        ]

        return render_template(
            'index.html', data=data, delayed=delayed, summary=summary,
            headers=headers, chart=chart, security_headers=security_headers,
            locations=locations, messages=messages, attachments=attachments
        )
    else:
        return render_template('index.html')
