from flask import (
    Flask,
    request,
    render_template,
    jsonify,
)

from utils import get_result, SECRET_KEY


app = Flask(__name__, template_folder='.')
app.secret_key = SECRET_KEY


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/result', methods=['POST'])
def result():
    """Accept a valid playlist id and return its total duration."""
    playlist = request.get_json(silent=True).get('playlist')
    result = get_result(playlist)
    duration = result.get('duration')
    if duration:
        return jsonify({'duration': duration})
    return jsonify({})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
