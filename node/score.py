# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.


''' Score из БД'''
from random import randint
from node.db import DB, Score, Suffix
from zold.time import DatetimeTime


class DbScore:
	''' Один Score, вычитываемый из БД '''
	def __init__(self, record):
		self.record = record

	# @todo #51 Префиксная часть Score должна представлять из себя объект.
	#  Строка плохо подходит для поиска по базе.
	#  Приходится брать json и доставать из него поля для поиска.
	def prefix(self):
		''' Префиксная часть Score '''
		return ' '.join((
			str(DatetimeTime(self.record.time)),
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

	def __str__(self):
		return ' '.join(
			[
				str(DatetimeTime(self.record.time)),
				self.record.host,
				str(self.record.port),
				self.record.invoice,
			] + self.suffixes()
		)

	def json(self):
		''' Унифицированное json представление '''
		return {
			'time': str(DatetimeTime(self.record.time)),
			'host': self.record.host,
			'port': self.record.port,
			'invoice': self.record.invoice,
			'suffixes': self.suffixes(),
			'strength': self.record.strength
		}


# @todo #51 Это утилитный класс, служит только для записи Score в БД.
#  По сути это такая функция. Надо взглянуть на это с другой стороны
#  и сделать сохранение в БД более объектным
class DbSavedScore:
	''' Сохраненный score, не забудьте вызвать метод save '''
	def __init__(self, score):
		self.score = score

	def save(self):
		''' Сохранение, имеющиеся записи не трогаются. '''
		jscore = self.score.json()
		# @todo #51 Лучше использовать id, поскольку по времени,
		#  полученному через json она ничего не найдет...
		dbscore = Score.query.filter_by(
			**{k: jscore[k] for k in ('host', 'port', 'invoice')}
		).first()
		if dbscore is None:
			raise RuntimeError("Score not found")
		for suffix in self.score.suffixes():
			if Suffix.query.filter_by(value=suffix, score_id=dbscore.id).count() == 0:
				DB.session.add(Suffix(suffix, dbscore.id))
		DB.session.commit()


class DbScores:
	''' Список всех Score из БД '''
	def __iter__(self):
		return (DbScore(s) for s in Score.query.all())

	def __bool__(self):
		return Score.query.count() != 0


class AtLeastOneDbScores:
	''' DbScores как минимум из одного Score '''
	def __init__(self, scores, config):
		self.scores = scores
		self.config = config

	def __iter__(self):
		if self.scores:
			yield from self.scores
		else:
			key_pos = randint(0, len(self.config['PUBLIC_KEY']) - 8)
			score = Score(
				self.config['HOST'],
				self.config['PORT'],
				''.join((
					self.config['PUBLIC_KEY'][key_pos:key_pos + 8],
					'@',
					self.config['WALLET']
				)),
				self.config['STRENGTH']
			)
			DB.session.add(score)
			DB.session.commit()
			yield DbScore(score)
