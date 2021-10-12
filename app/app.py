from flask import Flask, request, render_template, redirect

from utils import get_playlist_id, get_result


app = Flask(__name__, template_folder='.')


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        playlist = request.form.get('playlist')
        playlist_id = get_playlist_id(playlist)
        if not playlist_id:
            # flash an error
            return redirect(request.url)
        else:
            result = get_result(playlist_id)
            return render_template('index.html', result=result)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
