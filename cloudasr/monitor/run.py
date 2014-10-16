from flask import Flask, request, jsonify, render_template
from flask.ext.socketio import SocketIO, emit, session
import os
app = Flask(__name__)
app.config['DEBUG'] = True
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8001)
