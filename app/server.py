from flask import Flask, render_template, request, jsonify
from background_asr import recognize_wav

app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recognize', methods=['POST'])
def recognize():
    response = recognize_wav(request.data)

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
