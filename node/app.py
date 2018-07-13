# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' WEB интерфейс узла '''

from flask import Flask, jsonify, request, Response
from flask_api import status
from werkzeug.exceptions import NotAcceptable, BadRequest
from zold.score import StrongestScore, NextScore, ScoreHash, ScoreValid
from node.db import DB
from node.score import DbSavedScore, DbScores, AtLeastOneDbScores
from node.wallet import DbWallet


class JsonResponse(Response):
	''' Возвращаем JSON '''
	@classmethod
	def force_type(cls, response, environ=None):
		if isinstance(response, dict):
			response = jsonify(response)
		return super(JsonResponse, cls).force_type(response, environ)


APP = Flask(__name__)
APP.response_class = JsonResponse
APP.config.from_object('node.config')
DB.init_app(APP)
with APP.app_context():
	DB.create_all()


@APP.after_request
def after_request(response):
	''' Добавляем кастомный HTTP заголовок '''
	response.headers.add('X-Zold-Version', '0.0.0')
	return response


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
	return data


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
	data = {}
	return data


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
	return data


@APP.route('/wallet/<wallet_id>', methods=['GET'])
def api_get_wallet(wallet_id):
	''' Содержимое кошелька '''
	try:
		data = {
			'version': '0.0.0',
			'protocol': '1',
			'id': wallet_id,
			'body': DbWallet(wallet_id).body()
		}
	except RuntimeError:
		data = {}
		return data, 404
	return data


@APP.route('/wallet/<wallet_id>', methods=['PUT'])
def api_put_wallet(wallet_id):
	''' Обновление содержимого кошелька '''
	# @todo #7 Необходимо проверять содержимое запроса и
	#  сверять с содержимым кошелька.
	DbWallet(wallet_id, request.data.decode('utf8')).save()
	data = {
		'version': '0.0.0',
		'protocol': '1',
		'id': wallet_id,
		'score': StrongestScore(AtLeastOneDbScores(DbScores(), APP.config)).json()
	}
	# @todo #68 Сервер должен возвращать HTTP_ACCEPTED, в соответствии с WP.
	#  Но текущий клиент рассчитывает, что сервер отвечает кодом HTTP_200_OK.
	#  Достоточно сложно будет перейти с одного на другой.
	#  Клиент должен будет поддерживать оба.
	return data, status.HTTP_200_OK


if __name__ == '__main__':
	APP.run(debug=True, host='0.0.0.0', port=5000)
