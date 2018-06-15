from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/', methods=['GET'])
def api_root():
    data = {
        "version": "0.6.1",
        "score": {
            "value": 3,
            "time": "2017-07-19T21:24:51Z",
            "host": "b2.zold.io",
            "port": 4096,
            "invoice": "THdonv1E@0000000000000000",
            "suffixes": ["4f9c38", "49c074", "24829a"],
            "strength": 6
       }
    }

    resp = jsonify(data)
    resp.status_code = 200
    resp.headers['X-Zold-Version'] = '0.0.0'

    return resp


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
