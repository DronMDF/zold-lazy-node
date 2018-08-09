# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

'''
Характеристики Score
'''

import hashlib


class ScoreValue:
	''' Количество валидных суффиксов - это значение Score '''
	def __init__(self, score, config):
		self.score = score
		self.config = config

	def __int__(self):
		prefix = self.score.prefix()
		value = 0
		for suffix in self.score.suffixes():
			prefix = hashlib.sha256((prefix + ' ' + suffix).encode('ascii')).hexdigest()
			if not prefix.endswith('0' * self.config['STRENGTH']):
				break
			value += 1
		return value


class ScoreHash:
	''' Последний хеш Score. Если суффиксов нет, то возвращается префикс '''
	def __init__(self, score, config):
		self.score = score
		self.config = config

	# @todo #65: ScoreHash не должен проверять промежуточные хеши на валидность.
	#  Для этого у нас есть ScoreValid
	def __str__(self):
		prefix = self.score.prefix()
		for suffix in self.score.suffixes():
			prefix = hashlib.sha256((prefix + ' ' + suffix).encode('ascii')).hexdigest()
			if not prefix.endswith('0' * self.config['STRENGTH']):
				raise RuntimeError("Невалидный Score")
		return prefix


class ScoreValid:
	''' Вспомогательный класс транслирующийся в True, если score валиден '''
	def __init__(self, score, config):
		self.score = score
		self.config = config

	def __bool__(self):
		try:
			str(ScoreHash(self.score, self.config))
		except Exception:
			return False
		return True
