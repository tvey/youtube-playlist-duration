from flask import Flask, request, render_template, redirect, flash, jsonify

from utils import get_playlist_id, get_result, SECRET_KEY


app = Flask(__name__, template_folder='.')
app.secret_key = SECRET_KEY


@app.route('/', methods=['GET', 'POST'])
def home():
    # if request.method == 'POST':
    #     playlist = request.form.get('playlist')
    #     playlist_id = get_playlist_id(playlist)
    #     if not playlist_id:
    #         flash('Please add a valid playlist link or id.')
    #         return redirect(request.url)
    #     else:
    #         result = get_result(playlist_id)
    #         return render_template(
    #             'index.html', result=result, playlist=playlist
    #         )
    return render_template('index.html')


@app.route('/result', methods=['GET'])
def result():
    return jsonify(123)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
