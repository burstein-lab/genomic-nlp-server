import json
from flask import Flask, jsonify
from flask_cors import CORS

from coords import Point


# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/')
def hello():
    return 'Hello world!'


# sanity check route
@app.route("/ping", methods=["GET"])
def ping_pong():
    return jsonify("pong!")


@app.route('/points')
def points():
    result = []
    for i in range(1000):
        result.append(Point(i / 100, i / 100, str(i)).todict())

    return json.dumps(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
