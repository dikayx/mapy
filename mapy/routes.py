import os
import tempfile

from flask import Blueprint, render_template, request, send_file, abort
from werkzeug.utils import secure_filename

from mapy.utils import process_email_headers, extract_ip_geolocations, extract_message_data


blueprint = Blueprint('mapy', __name__)

@blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        mail_data = request.form['headers'].strip()
        data, delayed, summary, headers, chart = process_email_headers(mail_data)
        locations = extract_ip_geolocations(mail_data)
        messages, attachments = extract_message_data(mail_data)

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


@blueprint.route('/download/<filename>')
def download_file(filename):
    """
    Endpoint to download an attachment file.

    :param filename: The name of the file to be downloaded.
    """
    safe_filename = secure_filename(filename)
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, safe_filename)

    if not os.path.exists(file_path):
        abort(404, description="File not found")

    return send_file(file_path, as_attachment=True)
