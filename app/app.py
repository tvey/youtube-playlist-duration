from flask import (
    Flask,
    request,
    render_template,
    redirect,
    flash,
    url_for,
    jsonify,
)

from utils import get_playlist_id, get_result, SECRET_KEY


app = Flask(__name__, template_folder='.')
app.secret_key = SECRET_KEY


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        playlist_input = request.form.get('playlist')
        if not playlist_input:
            flash('This value cannot be empty.')
            return redirect(url_for('home'))
        playlist_id = get_playlist_id(playlist_input)
        if not playlist_id:
            flash('Please add a valid playlist link or id.')
            return redirect(url_for('home'))
    return render_template('index.html')


@app.route('/result', methods=['POST'])
def result():
    playlist_input = request.get_json().get('playlist')
    playlist_id = get_playlist_id(playlist_input)
    result = get_result(playlist_id)
    return jsonify({'duration': result})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
