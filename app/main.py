import os

import dotenv
from flask import (
    Flask,
    request,
    render_template,
    jsonify,
)

from utils import get_result

dotenv.load_dotenv()


def create_app():
    app = Flask(__name__, template_folder='.')
    app.config.from_object(__name__)
    app.config.update(
        {
            'SECRET_KEY': os.environ.get('SECRET_KEY'),
            'DEBUG': os.environ.get('DEBUG'),
        }
    )
    return app


app = create_app()


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/result', methods=['POST'])
def result():
    """Accept a playlist id and return a jsonified result from get_result()."""
    playlist = request.get_json(silent=True).get('playlist')
    result = get_result(playlist)
    return jsonify(result)


if __name__ == '__main__':
    app.run()
