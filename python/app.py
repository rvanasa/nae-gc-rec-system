import os
import json
from flask import Flask, request, send_file

from recs import Recsystem

DIR = os.path.abspath('..')
WWW_BASE = DIR + '/www'
QS_BASE = DIR + '/data/Qs'

# maybe we could pass these as request parameters eventually
grade = 4
test = 'MCAS'

# rc = Recsystem(QS_BASE, grade, test)

app = Flask(__name__)


@app.route('/')
def show_index():
	return send_file(WWW_BASE + '/index.html')


@app.route('/<path:path>')
def show_file(path):
  return send_file(WWW_BASE + '/' + path)


@app.route('/api/question', methods=['GET'])
def get_question():
	# retrieve user from query string, TODO migrate to using authentication
	user_id = request.args.get('user')
	
	print user_id
	
	return json.dumps({
		'text': 'What color is the sky?',
		'options': [{
			'id': 'A',
			'text': 'Sarcoline'
		}, {
			'id': 'B',
			'text': 'Smaragdine'
		}, {
			'id': 'C',
			'text': 'Glaucous'
		}, {
			'id': 'D',
			'text': 'Coquelicot'
		}]
	})


@app.route('/api/answer', methods=['POST'])
def post_answer():
	user_id = request.args.get('user')
	
	# letter corresponding to selected answer (e.g. A, B, C)
	selected = request.args.get('selected')
	
	return json.dumps({
		'correct': 'C'
	})
