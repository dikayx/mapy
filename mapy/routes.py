from flask import Blueprint, render_template, request

blueprint = Blueprint('mapy', __name__)


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return render_template('index.html', result='Hello, World!')
    return render_template('index.html')