# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' WEB интерфейс узла '''

from flask import Flask, jsonify, request
from flask_api import status
from werkzeug.exceptions import NotAcceptable, BadRequest
from zold.score import StrongestScore, NextScore, ScoreHash, ScoreValid
from node.db import DB
from node.score import DbSavedScore, DbScores, AtLeastOneDbScores
from node.wallet import DbWallet

APP = Flask(__name__)
APP.config.from_object('node.config')
DB.init_app(APP)
with APP.app_context():
	DB.create_all()


@APP.route('/', methods=['GET'])
def api_root():
	''' Статус ноды '''
	# @todo #3 version и X-Zold-Version, должны содержать текущую версию zold.
	#  Но хранить ее где-то будет не очень удобно.
	#  Предлагаю использовать версию, которую выдают соседние сервера.
	#  Для этого ее видимо необходимо хранить в БД.
	#  Но пока можно прописать константу.
	data = {
		'version': '0.6.1',
		'score': StrongestScore(AtLeastOneDbScores(DbScores(), APP.config)).json(),
		'farm': {
			'current': [
				str(ScoreHash(s)) for s in DbScores()
			]
		}
	}

	resp = jsonify(data)
	resp.status_code = 200
	resp.headers['X-Zold-Version'] = '0.0.0'

	return resp


@APP.route('/score', methods=['POST'])
def api_score():
	''' Загрузка суффиксов на сервер '''
	suffix = request.json.get('suffix', None)
	if suffix is None:
		raise BadRequest("Bad request")
	score = next((
		p
		for p in (NextScore(s, suffix) for s in DbScores())
		if ScoreValid(p)
	), None)
	if score is None:
		raise NotAcceptable("Wrong suffix")
	DbSavedScore(score).save()
	resp = jsonify({})
	resp.status_code = 200
	resp.headers['X-Zold-Version'] = '0.0.0'
	return resp


@APP.route('/remotes', methods=['GET'])
def api_remotes():
	''' Список известных и проверенных нод '''
	data = {
		"version": "0.13.5",
		"all": [
			{"host": "b2.zold.io", "port": 4096, "score": 0},
			{"host": "b1.zold.io", "port": 80, "score": 0}
		]
	}
	# @todo #4 Это копипаста... я вижу эти три строки уже два раза.
	#  И подозреваю, что будет больше. Необходимо вынести этот функционал
	#  в отдельный класс.  К тому же заголовок тоже будет больше...
	#  Есть запрос 228 на заголовок X-Zold-Network.
	#  zold потенциально поддерживает разные сети.
	resp = jsonify(data)
	resp.status_code = 200
	resp.headers['X-Zold-Version'] = '0.0.0'

	return resp


@APP.route('/wallet/<wallet_id>', methods=['GET'])
def api_get_wallet(wallet_id):
	''' Содержимое кошелька '''
	try:
		resp = jsonify({
			'version': '0.0.0',
			'protocol': '1',
			'id': wallet_id,
			'body': DbWallet(wallet_id).body()
		})
		resp.status_code = 200
	except RuntimeError:
		resp = jsonify({})
		resp.status_code = 404
	resp.headers['X-Zold-Version'] = '0.0.0'
	return resp


@APP.route('/wallet/<wallet_id>', methods=['PUT'])
def api_put_wallet(wallet_id):
	''' Обновление содержимого кошелька '''
	# @todo #7 Необходимо проверять содержимое запроса и
	#  сверять с содержимым кошелька.
	DbWallet(wallet_id, request.data.decode('utf8')).save()
	resp = jsonify({
		'version': '0.0.0',
		'protocol': '1',
		'id': wallet_id,
		'score': StrongestScore(AtLeastOneDbScores(DbScores(), APP.config)).json()
	})
	# @todo #68 Сервер должен возвращать HTTP_ACCEPTED, в соответствии с WP.
	#  Но текущий клиент рассчитывает, что сервер отвечает кодом HTTP_OK.
	#  Достоточно сложно будет перейти с одного на другой.
	#  Клиент должен будет поддерживать оба.
	resp.status_code = status.HTTP_200_OK
	resp.headers['X-Zold-Version'] = '0.0.0'
	return resp


if __name__ == '__main__':
	APP.run(debug=True, host='0.0.0.0', port=5000)
