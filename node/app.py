# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' WEB интерфейс узла '''

import itertools
from flask import Flask, jsonify, request, Response
from flask_api import status
from werkzeug.exceptions import NotAcceptable, BadRequest
from zold.score import NextScore, ValueScore, XZoldScore
from zold.scores import WeakScores, NewerThenScores
from zold.score_props import (
	ScoreHash,
	ScoreJson,
	ScoreString,
	ScoreValid,
	ScoreValue
)
from zold.time import AheadTime
from zold.transaction import (
	OrderedTransactions,
	OutgoingTransactions,
	IncomingTransactions,
	TransactionsAmount,
	TransactionString,
	TransactionValid
)
from zold.wallet import StringWallet, TransactionWallet
from node.db import DB, TransactionDstStatus
from node.score import AtLeastOneDbScores, DbScores, DbSavedScore, MainScore
from node.remote import DbRemotes, IsRemoteUpdated
from node.transaction import DbTransactions
from node.wallet import DbWallets, DbWanted


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
	score = MainScore(APP.config)
	response.headers.add('X-Zold-Version', APP.config['ZOLD_VERSION'])
	# @todo #175 Для X-Zold-Score, нужен специальный XScoreString
	response.headers.add(
		'X-Zold-Score',
		'%u/%u: %s' % (
			ScoreValue(score, APP.config),
			APP.config['STRENGTH'],
			ScoreString(score)
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
		'hours_alive': 1,
		'load': 0.0,
		'memory': 4 * 1024 * 1024,
		'nscore': 1,
		'platform': 'null',
		'protocol': 2,
		# @todo #126 Передать реальное количество имеющихся узлов.
		'remotes': 20,
		'score': ValueScore(MainScore(APP.config), APP.config).json(),
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
def api_tasks():
	''' Список задач для помошников '''
	# Проверка непроверенных входящих транзакций
	for wnt in DbWanted():
		for tnx in DbTransactions().select(
			dst_id=wnt.who(),
			dst_status=TransactionDstStatus.UNKNOWN
		):
			DbTransactions().update(
				tnx,
				TransactionDstStatus.GOOD
				if tnx.prefix() in DbWallets(APP.config).wallet(wnt.who()).public()
				else TransactionDstStatus.BAD
			)
		if str(TransactionString(wnt.transaction())) in (
			str(TransactionString(t))
			for t in DbTransactions().incoming(wnt.who())
		):
			wnt.remove()
	# @todo #155 Удалить старые Score из таблиц
	#  Здесь хорошее место, чтобы потратить немного времени на наведение порядка
	data = {
		'tasks': list(itertools.chain(
			[
				{'type': 'mining', 'base': str(ScoreHash(s, APP.config))}
				for s in WeakScores(
					AtLeastOneDbScores(
						NewerThenScores(DbScores(), AheadTime(12)),
						APP.config
					),
					16,
					APP.config
				)
			],
			[
				{
					'type': 'wanted',
					'id': r.json()['id'],
					'prefix': r.json()['prefix'],
					'transaction': ''
				}
				for r in DbRemotes()
				if r.json()['id'] not in [w.id() for w in DbWallets(APP.config)]
			],
			[
				{
					'type': 'wanted',
					'id': t.bnf(),
					'prefix': t.prefix(),
					'transaction': str(TransactionString(t))
				}
				for t in DbTransactions().select(dst_status=TransactionDstStatus.UNKNOWN)
			],
			[
				{
					'type': 'wanted',
					'id': w.id(),
					'transaction': str(TransactionString(w.transaction()))
				}
				for w in DbWanted()
			]
		))
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
		'score': ScoreJson(MainScore(APP.config), APP.config['STRENGTH']).json()
	}


@APP.route('/wallet/<wallet_id>', methods=['GET'])
def api_get_wallet(wallet_id):
	''' Содержимое кошелька '''
	try:
		data = {
			'protocol': APP.config['ZOLD_PROTOCOL'],
			'version': APP.config['ZOLD_VERSION'],
			'id': wallet_id,
			'body': str(TransactionWallet(
				DbWallets(APP.config).wallet(wallet_id),
				*OrderedTransactions(
					itertools.chain(
						DbTransactions().select(src_id=wallet_id),
						DbTransactions().incoming(wallet_id)
					)
				)
			)),
			'score': ScoreJson(MainScore(APP.config), APP.config['STRENGTH']).json()
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
	wallet = StringWallet(request.get_data().decode('utf8'))
	try:
		DbWallets(APP.config).wallet(wallet.id())
	except RuntimeError:
		DbWallets(APP.config).add(wallet)
	# Проверка непроверенных входящих транзакций
	unchecked = DbTransactions().select(
		dst_id=wallet.id(),
		dst_status=TransactionDstStatus.UNKNOWN
	)
	for tnx in unchecked:
		DbTransactions().update(
			tnx,
			TransactionDstStatus.GOOD
			if tnx.prefix() in wallet.public()
			else TransactionDstStatus.BAD
		)
	# Задачи на поиск неизвестных отправителей
	for tnx in IncomingTransactions(wallet.transactions()):
		# @todo #155 Поиск входяших транзакций не оптимален в плане скорости
		if str(TransactionString(tnx)) not in (
			str(TransactionString(t))
			for t in DbTransactions().incoming(wallet.id())
		):
			# @todo #155 В списке wanted необходимо добавить резон
			#  Резон описывает потребность в поиске. Когда эта
			#  потребность удовлетворена - запись можно стирать.
			DbWanted().add(tnx.bnf(), tnx, wallet.id())
	# Определение доступного баланса
	if wallet.id() == '0000000000000000':
		limit = 0xffffffffffffffff
	else:
		limit = int(TransactionsAmount(DbTransactions().incoming(wallet.id())))
	# @todo #157 При рассчете баланса необходимо учитывать транзакции из БД,
	#  они могут быть упущены в кошельке
	for tnx in OrderedTransactions(OutgoingTransactions(wallet.transactions())):
		if limit < abs(tnx.amount()):
			break
		if TransactionValid(tnx, wallet):
			DbTransactions().add(wallet.id(), tnx)
			limit -= abs(tnx.amount())

	data = {
		'version': APP.config['ZOLD_VERSION'],
		'protocol': APP.config['ZOLD_PROTOCOL'],
		'id': wallet_id,
		'score': ScoreJson(MainScore(APP.config), APP.config['STRENGTH']).json()
	}
	# @todo #68 Сервер должен возвращать HTTP_ACCEPTED, в соответствии с WP.
	#  Но текущий клиент рассчитывает, что сервер отвечает кодом HTTP_200_OK.
	#  Достоточно сложно будет перейти с одного на другой.
	#  Клиент должен будет поддерживать оба.
	return data, status.HTTP_200_OK
