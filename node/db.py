# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Модель данных (схема БД) '''

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()


class Score(DB.Model):
	''' Таблица Score для узла '''
	id = DB.Column(DB.Integer, primary_key=True)
	time = DB.Column(DB.DateTime)
	host = DB.Column(DB.String(64))
	port = DB.Column(DB.Integer)
	invoice = DB.Column(DB.String(64))
	suffixes = DB.relationship('Suffix', backref='score', lazy=True)


class Suffix(DB.Model):
	''' Суффиксы для Score's '''
	id = DB.Column(DB.Integer, primary_key=True)
	value = DB.Column(DB.String(32))
	time = DB.Column(DB.DateTime)
	score_id = DB.Column(DB.Integer, DB.ForeignKey('score.id'))

	def __init__(self, value):
		self.value = value
		self.time = datetime.now()