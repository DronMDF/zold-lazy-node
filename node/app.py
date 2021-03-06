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
from zold.time import AheadTime, NowTime
from zold.transaction import (
	OrderedTransactions,
	IncomingTransactions,
	TransactionsAmount,
	TransactionIn,
	TransactionString,
)
from zold.wallet import StringWallet, TransactionWallet, WalletString
from node.db import DB, TransactionDstStatus
from node.score import AtLeastOneDbScores, DbScores, DbSavedScore, MainScore
from node.remote import DbRemotes, IsRemoteUpdated
from node.transaction import DbTransactions, LimitedNewTransactions
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
	response.headers.add('Access-Control-Allow-Origin', '*')
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
		'wallets': DbWallets(APP.config).count()
	}
	return data


@APP.route('/version', methods=['GET'])
def api_version():
	''' версия ноды '''
	return APP.config['ZOLD_VERSION']


@APP.route('/tasks', methods=['GET'])
def api_tasks():
	''' Список задач для помошников '''
	# Проверка непроверенных исходящих
	for tnx in DbTransactions().select(dst_status=TransactionDstStatus.UNKNOWN):
		try:
			if tnx.prefix() in DbWallets(APP.config).wallet(tnx.bnf()).public():
				tnx.update(TransactionDstStatus.GOOD)
			else:
				tnx.update(TransactionDstStatus.BAD)
		except Exception:
			pass
	for wnt in DbWanted():
		if TransactionIn(wnt.transaction(), DbTransactions().incoming(wnt.who())):
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
					'transaction': '',
					'reason': 'remote'
				}
				for r in DbRemotes()
				if r.json()['id'] not in [w.id() for w in DbWallets(APP.config)]
			],
			[
				{
					'type': 'wanted',
					'id': t.bnf(),
					'prefix': t.prefix(),
					'transaction': str(TransactionString(t)),
					'reason': 'dst unknown',
					'who': t.src()
				}
				for t in DbTransactions().select(dst_status=TransactionDstStatus.UNKNOWN)
			],
			[
				{
					'type': 'wanted',
					'id': w.id(),
					'transaction': str(TransactionString(w.transaction())),
					'reason': 'wanted',
					'who': w.who()
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
		wallet = DbWallets(APP.config).wallet(wallet_id)
		for tnx in DbTransactions().unapproved(wallet_id):
			if tnx.prefix() in wallet.public():
				tnx.update(TransactionDstStatus.GOOD)
		# @todo #215 Список транзакций должен формироваться в DbWallet
		transactions = list(
			OrderedTransactions(
				itertools.chain(
					DbTransactions().select(src_id=wallet_id),
					DbTransactions().incoming(wallet_id)
				)
			)
		)
		return {
			'protocol': APP.config['ZOLD_PROTOCOL'],
			'version': APP.config['ZOLD_VERSION'],
			'id': wallet_id,
			'body': str(WalletString(TransactionWallet(wallet, *transactions))),
			'mtime': str(transactions[-1].time() if transactions else NowTime()),
			'score': ScoreJson(MainScore(APP.config), APP.config['STRENGTH']).json()
		}
	except RuntimeError:
		return {}, 404


@APP.route('/wallet/<wallet_id>/balance', methods=['GET'])
def api_get_wallet_balance(wallet_id):
	''' Баланс кошелька '''
	transactions = list(itertools.chain(
		DbTransactions().select(src_id=wallet_id),
		DbTransactions().incoming(wallet_id)
	))
	if transactions:
		return str(int(TransactionsAmount(transactions)))
	return {}, 404


@APP.route('/wallet/<wallet_id>', methods=['PUT'])
def api_put_wallet(wallet_id):
	''' Обновление содержимого кошелька '''
	wallet = StringWallet(request.get_data().decode('utf8'))
	if wallet.id() != wallet_id:
		return {}, status.HTTP_400_BAD_REQUEST
	try:
		dbwallet = DbWallets(APP.config).wallet(wallet.id())
		if dbwallet.public() != wallet.public():
			return {}, status.HTTP_400_BAD_REQUEST
	except RuntimeError:
		DbWallets(APP.config).add(wallet)
	# Проверка непроверенных входящих транзакций
	for tnx in DbTransactions().unapproved(wallet_id):
		if tnx.prefix() in wallet.public():
			tnx.update(TransactionDstStatus.GOOD)
	# Все Wanted для данного кошелька стираются
	for wanted in (w for w in DbWanted() if w.id() == wallet.id()):
		wanted.remove()
	# Задачи на поиск неизвестных отправителей
	for txn in IncomingTransactions(wallet.transactions()):
		if all((
			txn.prefix() in wallet.public(),
			not TransactionIn(txn, DbTransactions().incoming(wallet.id())),
			txn.bnf() not in [w.id() for w in DbWanted()]
		)):
			DbWanted().add(txn.bnf(), txn, wallet.id())
	# Определение доступного баланса
	if wallet.id() == '0000000000000000':
		limit = 0xffffffffffffffff
	else:
		limit = int(TransactionsAmount(DbTransactions().incoming(wallet.id())))
	for tnx in LimitedNewTransactions(wallet, limit):
		DbTransactions().add(wallet.id(), tnx)
	# @todo #68 Сервер должен возвращать HTTP_ACCEPTED, в соответствии с WP.
	#  Но текущий клиент рассчитывает, что сервер отвечает кодом HTTP_200_OK.
	#  Достоточно сложно будет перейти с одного на другой.
	#  Клиент должен будет поддерживать оба.
	return {
		'version': APP.config['ZOLD_VERSION'],
		'protocol': APP.config['ZOLD_PROTOCOL'],
		'id': wallet_id,
		'score': ScoreJson(MainScore(APP.config), APP.config['STRENGTH']).json()
	}, status.HTTP_200_OK
