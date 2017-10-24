"""
TODO:
    Connect to frontend
    Look through some of the weirder errors
        + (negative percentage corrects?)
"""

import os
import json
from flask import Flask, request
from recs import Recsystem

DIR = os.path.abspath('..')
rc = Recsystem(DIR)
app = Flask(__name__)


@app.route('/api/question', methods=['GET'])
def get_question():
    q, a, b, c, d = rc.send_question()
    last_percent = rc.send_q_stats()

    return json.dumps({
        'question': q,
        'last_percent':last_percent,
        'answers': [{
            'id': 'A',
            'text': a
        }, {
            'id': 'B',
            'text': b
        }, {
            'id': 'C',
            'text': c
        }, {
            'id': 'D',
            'text': d
        }]
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    percent, qs_answered = rc.send_user_stats()

    return json.dumps({
        'qs_answered': qs_answered,
        'percentage':percent
    })


# {"answer": "C"}
@app.route('/api/answer', methods=['POST'])
def post_answer():
    j = request.json
    rc.prep_next_q(j['answer'])
    return ('', 200)


# {"username": "ttrojan77"}
@app.route('/api/login', methods=['POST'])
def post_login():
    j = request.json
    rc.init_user(j['username'])
    return ('', 200)


if __name__ == '__main__':
    app.run()
