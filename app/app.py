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
    playlist = request.get_json().get('playlist')
    if playlist != -1:
        result = get_result(playlist)
        if result:
            return jsonify({'duration': result})
    return jsonify({})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
