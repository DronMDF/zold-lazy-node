# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.


''' Score из БД'''
from node.db import DB, Score, Suffix


class DbScore:
	''' Один Score, вычитываемый из БД '''
	def __init__(self, record):
		self.record = record

	def prefix(self):
		''' Префиксная часть Score '''
		return ' '.join((
			# @todo #41 Формат даты времени не соответствует WP
			self.record.time.isoformat(),
			self.record.host,
			str(self.record.port),
			self.record.invoice
		))

	def suffixes(self):
		''' Список суффиксов '''
		return [
			s.value
			for s in Suffix.query.filter(Suffix.score_id == self.record.id).all()
		]

	def json(self):
		''' Унифицированное json представление '''
		return {
			'time': self.record.time.isoformat(),
			'host': self.record.host,
			'port': self.record.port,
			'invoice': self.record.invoice,
			'suffixes': self.suffixes()
		}


class DbScores:
	''' Список всех Score из БД '''
	def __iter__(self):
		return (DbScore(s) for s in Score.query.all())

	def __bool__(self):
		return Score.query.count() != 0

	def new_suffix(self, suffix):
		''' Добавляем новый суффикс в БД '''
		DB.session.add(Suffix(suffix))
		DB.session.commit()


class AtLeastOneDbScores:
	''' DbScores как минимум из одного Score '''
	def __init__(self, scores):
		self.scores = scores

	def __iter__(self):
		if self.scores:
			yield from self.scores
		else:
			# @todo #41 Необходимо наполнить новый Score Адекватными данными
			score = Score('1.2.3.4', 4096, 'invoice')
			DB.session.add(score)
			DB.session.commit()
			yield DbScore(score)
