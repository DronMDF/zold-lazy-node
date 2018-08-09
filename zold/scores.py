# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

'''
Списки Score (Scores)
Интерфейс списка соответствует концепции iterable
'''

from .score_props import ScoreValue
from .time import StringTime


class WeakScores:
	''' Подмножество Score, которые не достигли указанного уровня '''
	def __init__(self, scores, level, config):
		self.scores = scores
		self.level = level
		self.config = config

	def __iter__(self):
		return (
			s
			for s in self.scores
			if int(ScoreValue(s, self.config)) < self.level
		)

	def __bool__(self):
		return any((
			int(ScoreValue(s, self.config)) < self.level
			for s in self.scores
		))


class NewerThenScores:
	'''
	Фильтрованный список содержащий только score
	поднее указанного момента времени
	'''
	def __init__(self, scores, time):
		self.scores = scores
		self.time = time

	def __iter__(self):
		yield from ((
			s
			for s in self.scores
			if StringTime(s.json()['time']).as_datetime() >= self.time.as_datetime()
		))
