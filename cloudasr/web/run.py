import os
from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = "12345"
app.config['DEBUG'] = True

@app.route('/demo')
def demo():
    return render_template('demo.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
