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
	wallet_id = DB.Column(DB.String(16), unique=True, nullable=False)
	network = DB.Column(DB.Text)
	public = DB.Column(DB.Text)

	def __init__(self, wallet_id, body):
		self.wallet_id = wallet_id
		bdata = body.split('\n')
		self.network = bdata[0]
		self.public = bdata[3]


class TransactionStatus(enum.Enum):
	''' Состояние транзакции с каждой стороны '''
	UNKNOWN = 0
	GOOD = 9


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

	src_status = DB.Column(DB.Enum())
	dst_status = DB.Column(DB.Enum())
