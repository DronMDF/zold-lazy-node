# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' WEB интерфейс узла '''

from flask import Flask, jsonify, request, Response
from flask_api import status
from werkzeug.exceptions import NotAcceptable, BadRequest
from zold.score import NextScore, StrongestScore, ValueScore, XZoldScore
from zold.scores import WeakScores, NewerThenScores
from zold.score_props import ScoreHash, ScoreValid, ScoreValue
from zold.time import AheadTime
from node.db import DB
from node.score import AtLeastOneDbScores, DbScores, DbSavedScore
from node.wallet import DbWallet
from node.remote import DbRemotes, IsRemoteUpdated


class JsonResponse(Response):
	''' Возвращаем JSON '''
	@classmethod
	def force_type(cls, response, environ=None):
		''' Формируем ответ сервера'''
		if isinstance(response, dict):
			response = jsonify(response)
		return super().force_type(response, environ)


APP = Flask(__name__)
APP.response_class = JsonResponse
APP.config.from_object('node.config')
DB.init_app(APP)
with APP.app_context():
	DB.create_all()


@APP.after_request
def after_request(response):
	''' Добавляем кастомный HTTP заголовок '''
	score = StrongestScore(
		AtLeastOneDbScores(NewerThenScores(DbScores(), AheadTime(24)), APP.config),
		APP.config
	)
	response.headers.add('X-Zold-Version', APP.config['ZOLD_VERSION'])
	response.headers.add(
		'X-Zold-Score',
		'%u/%u: %s' % (
			ScoreValue(score, APP.config),
			APP.config['STRENGTH'],
			score
		)
	)
	return response


@APP.route('/', methods=['GET'])
def api_root():
	''' Статус ноды '''
	# @todo #105 в случае некорректного формата X-Zold-Score
	#  не происходит сообщения об ошибке
	if 'X-Zold-Score' in request.headers:
		score = XZoldScore(request.headers['X-Zold-Score'])
		if int(ScoreValue(score, APP.config)) >= 3:
			if not IsRemoteUpdated(score, APP.config):
				raise RuntimeError('Unable to update remote by score')
	# @todo #66 Старые Score необходимо поудалять из БД
	data = {
		'cpus': 1,
		'entrance': {
			'history_size': 8,
			'queue': 0,
			'queue_age': 0,
			'speed': 0
		},
		'farm': {
			'current': [
				s.json()
				for s in WeakScores(
					AtLeastOneDbScores(
						NewerThenScores(DbScores(), AheadTime(12)),
						APP.config
					),
					16,
					APP.config
				)
			]
		},
		'hours_alive': 1,
		'load': 0.0,
		'memory': 4 * 1024 * 1024,
		'nscore': 1,
		'platform': 'null',
		'protocol': 2,
		# @todo #126 Передать реальное количество имеющихся узлов.
		'remotes': 20,
		'score': ValueScore(
			StrongestScore(
				AtLeastOneDbScores(NewerThenScores(DbScores(), AheadTime(24)), APP.config),
				APP.config
			),
			APP.config
		).json(),
		'threads': '1/1',
		'version': APP.config['ZOLD_VERSION'],
		# @todo #126 Передать реальное количество имеющихся кошельков.
		'wallets': 1
	}
	return data


@APP.route('/version', methods=['GET'])
def api_version():
	''' версия ноды '''
	return APP.config['ZOLD_VERSION']


@APP.route('/tasks', methods=['GET'])
def api_get_tasks():
	''' Список задач для помошников '''
	return {
		'tasks': [
			{'type': 'mining', 'base': str(ScoreHash(s, APP.config))}
			for s in WeakScores(
				AtLeastOneDbScores(
					NewerThenScores(DbScores(), AheadTime(12)),
					APP.config
				),
				16,
				APP.config
			)
		]
	}


@APP.route('/score', methods=['POST'])
def api_score():
	''' Загрузка суффиксов на сервер '''
	suffix = request.json.get('suffix', None)
	if suffix is None:
		raise BadRequest("Bad request")
	score = next((
		p
		for p in (
			NextScore(s, suffix)
			for s in NewerThenScores(DbScores(), AheadTime(24))
		)
		if ScoreValid(p, APP.config)
	), None)
	if score is None:
		raise NotAcceptable("Wrong suffix")
	DbSavedScore(score).save()
	data = {}
	return data


@APP.route('/remotes', methods=['GET'])
def api_remotes():
	''' Список известных и проверенных нод '''
	return {
		'version': APP.config['ZOLD_VERSION'],
		# @todo #105 Нужно выбрать только актуальные Remote (последних суток)
		'all': [r.json() for r in DbRemotes()],
		'score': StrongestScore(
			AtLeastOneDbScores(NewerThenScores(DbScores(), AheadTime(24)), APP.config),
			APP.config
		).json()
	}


@APP.route('/wallet/<wallet_id>', methods=['GET'])
def api_get_wallet(wallet_id):
	''' Содержимое кошелька '''
	try:
		data = {
			'protocol': '1',
			'version': APP.config['ZOLD_VERSION'],
			'id': wallet_id,
			'body': DbWallet(wallet_id).body(),
			'score': StrongestScore(
				AtLeastOneDbScores(NewerThenScores(DbScores(), AheadTime(24)), APP.config),
				APP.config
			).json()
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
	DbWallet(wallet_id, request.get_data().decode('utf8')).save()
	data = {
		'version': APP.config['ZOLD_VERSION'],
		'protocol': '1',
		'id': wallet_id,
		'score': StrongestScore(
			AtLeastOneDbScores(NewerThenScores(DbScores(), AheadTime(24)), APP.config),
			APP.config
		).json()
	}
	# @todo #68 Сервер должен возвращать HTTP_ACCEPTED, в соответствии с WP.
	#  Но текущий клиент рассчитывает, что сервер отвечает кодом HTTP_200_OK.
	#  Достоточно сложно будет перейти с одного на другой.
	#  Клиент должен будет поддерживать оба.
	return data, status.HTTP_200_OK


if __name__ == '__main__':
	APP.run(debug=True, host='0.0.0.0', port=5000)
