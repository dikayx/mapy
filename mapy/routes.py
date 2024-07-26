from flask import Blueprint, render_template, request

from mapy.utils import process_email_headers

blueprint = Blueprint('mapy', __name__)


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        mail_data = request.form['headers'].strip()
        r, delayed, summary, n, chart = process_email_headers(mail_data)
        security_headers = [
            'Received-SPF', 'Authentication-Results',
            'DKIM-Signature', 'ARC-Authentication-Results'
        ]
        return render_template(
            'index.html', data=r, delayed=delayed, summary=summary,
            n=n, chart=chart, security_headers=security_headers
        )
    else:
        return render_template('index.html')
