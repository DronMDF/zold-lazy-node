# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.


'''
Интерфейс Score:

score.prefix() - префиксная часть
score.suffixes() - суффиксы

str(score) - В виде строки
score.json() - в виде json

score.expired() - устарел

'''

import hashlib


class JsonScore:
	''' Этот Score конструируется из json '''
	def __init__(self, json):
		self.data = json

	def __str__(self):
		return ' '.join([self.prefix()] + self.suffixes())

	def json(self):
		''' В виде json '''
		return self.data

	def prefix(self):
		''' Префиксная часть Score '''
		return ' '.join((
			self.data['time'],
			self.data['host'],
			str(self.data['port']),
			self.data['invoice']
		))

	def suffixes(self):
		''' Список суффиксов'''
		return self.data['suffixes']


class StrongestScore:
	''' Самый мощный score из списка '''
	def __init__(self, scores):
		self.scores = scores

	def json(self):
		''' В виде json '''
		return max(self.scores, key=lambda s: ScoreValue(s).value()).json()


# @todo #51 ротестировать NextScore
class NextScore:
	''' Увеличенный Score на один суффикс больше, чем предыдущий '''
	def __init__(self, score, suffix):
		self.score = score
		self.suffix = suffix

	def prefix(self):
		''' Префикс как и у оригинального '''
		return self.score.prefix()

	def suffixes(self):
		''' А суффикс на один длиннее '''
		return self.score.suffixes() + [self.suffix]


class ScoreValue:
	''' Количество валидных суффиксов - это значение Score '''
	def __init__(self, score):
		self.score = score

	def value(self):
		''' Значение score (количество валидных суффиксов)'''
		prefix = self.score.prefix()
		value = 0
		for suffix in self.score.suffixes():
			prefix = hashlib.sha256((prefix + ' ' + suffix).encode('ascii')).hexdigest()
			if not prefix.endswith('0' * 6):
				break
			value += 1
		return value


class ScoreHash:
	''' Последний хеш Score. Если суффиксов нет, то возвращается префикс '''
	def __init__(self, score, strongest=6):
		self.score = score
		self.strongest = strongest

	def __str__(self):
		prefix = self.score.prefix()
		for suffix in self.score.suffixes():
			prefix = hashlib.sha256((prefix + ' ' + suffix).encode('ascii')).hexdigest()
			if not prefix.endswith('0' * self.strongest):
				raise RuntimeError("Невалидный Score")
		return prefix


# @todo #54 Протестировать ScoreValid
class ScoreValid:
	''' Вспомогательный класс транслирующийся в True, если score валиден '''
	def __init__(self, score, strength=6):
		self.score = score
		self.strength = strength

	def __bool__(self):
		try:
			str(ScoreHash(self.score, self.strength))
		except Exception:
			return False
		return True
