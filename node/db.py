# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Модель данных (схема БД) '''

import enum
from flask_sqlalchemy import SQLAlchemy
from zold.time import NowTime


DB = SQLAlchemy()


class Score(DB.Model):
	''' Таблица Score для узла '''
	id = DB.Column(DB.Integer, primary_key=True)
	time = DB.Column(DB.DateTime)
	host = DB.Column(DB.String(64))
	port = DB.Column(DB.Integer)
	invoice = DB.Column(DB.String(64))
	suffixes = DB.relationship('Suffix', backref='score', lazy=True)
	strength = DB.Column(DB.Integer)

	def __init__(self, host, port, invoice, strength):
		self.time = NowTime().as_datetime()
		self.host = host
		self.port = port
		self.invoice = invoice
		self.strength = strength


class Suffix(DB.Model):
	''' Суффиксы для Score's '''
	id = DB.Column(DB.Integer, primary_key=True)
	value = DB.Column(DB.String(32))
	time = DB.Column(DB.DateTime)
	score_id = DB.Column(DB.Integer, DB.ForeignKey('score.id'))

	def __init__(self, value, score_id):
		self.value = value
		self.time = NowTime().as_datetime()
		self.score_id = score_id


class Remote(DB.Model):
	'''
	Узел сети
	Узел довольно таки похож на Score,
	только содержит больше полей и ведет себя по другому.
	В случае прихода новой информации - узел обновляется.
	'''
	id = DB.Column(DB.Integer, primary_key=True)
	time = DB.Column(DB.DateTime)
	host = DB.Column(DB.String(64))
	port = DB.Column(DB.Integer)
	invoice = DB.Column(DB.String(64))
	score_value = DB.Column(DB.Integer)

	def __init__(self, host, port):
		self.host = host
		self.port = port


class Wallet(DB.Model):
	''' Кошелек '''
	id = DB.Column(DB.Integer, primary_key=True)
	wallet_id = DB.Column(DB.String(16), nullable=False)
	network = DB.Column(DB.Text, default='zold')
	public = DB.Column(DB.Text, nullable=False)

	def __init__(self, wallet_id, network, public):
		self.wallet_id = wallet_id
		self.network = network
		self.public = public


class WantedWallet(DB.Model):
	'''
	Кошелек, который необходимо найти
	В эту таблицу попадают кошельки, кторые являются источниками транзакций
	При этом данные о транзакции отсутствуют в БД. Мы не можем принимать
	эти транзакции, но должны оставить себе информацию для поиска.
	'''
	id = DB.Column(DB.Integer, primary_key=True)
	wallet_id = DB.Column(DB.String(16), nullable=False)
	network = DB.Column(DB.Text, default='zold')


class TransactionDstStatus(enum.Enum):
	''' Состояние транзакции относительно получателя '''
	UNKNOWN = 0
	BAD = 1
	GOOD = 2


class Transaction(DB.Model):
	''' Транзакция '''
	id = DB.Column(DB.Integer, primary_key=True)
	transact_id = DB.Column(DB.Integer)
	time = DB.Column(DB.DateTime)
	src_id = DB.Column(DB.String(16))
	dst_prefix = DB.Column(DB.String(32))
	dst_id = DB.Column(DB.String(16))
	# Размер суммы всегда положительный. Храним переводы.
	amount = DB.Column(DB.Integer)
	details = DB.Column(DB.Text)
	signature = DB.Column(DB.Text)

	# В БД попадают только транзакции с правильными сигнатурами.
	# Но кошелька получателя в тот момент может еще не быть.
	dst_status = DB.Column(DB.Enum(TransactionDstStatus))
