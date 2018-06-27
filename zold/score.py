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

score.valid() - Полностью валиден
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

	def valid(self):
		''' Проверка валидности Score '''
		prefix = self.prefix()
		for suffix in self.suffixes():
			prefix = hashlib.sha256((prefix + ' ' + suffix).encode('ascii')).hexdigest()
			if not prefix.endswith('0' * 6):
				return False
		return True


class StrongestScore:
	''' Самый мощный score из списка '''
	def __init__(self, scores):
		self.scores = scores

	def json(self):
		''' В виде json '''
		return max(self.scores, key=lambda s: ScoreValue(s).value()).json()


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
