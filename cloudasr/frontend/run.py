from flask import Flask, jsonify
app = Flask(__name__)


@app.route("/recognize", methods=['POST'])
def recognize_batch():
    return jsonify({
        "result": [
            {
                "alternative": [
                    {
                        "confidence": 1.0,
                        "transcript": "Hello World!"
                    },
                ],
                "final": True,
            },
        ],
        "result_index": 0,
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
