# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Модель данных (схема БД) '''

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


class Wallet(DB.Model):
	''' Кошелек '''
	id = DB.Column(DB.Integer, primary_key=True)
	wallet_id = DB.Column(DB.String(16))
	body = DB.Column(DB.UnicodeText())

	def __init__(self, wallet_id, body):
		self.wallet_id = wallet_id
		self.body = body
