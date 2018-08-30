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
import random
import re
import base58
from .score_props import ScoreHash, ScoreValue


# @todo #68 StringScore('<zold.score.StrongestScore object at 0x7f462d0>')
#  считается валидным. Вероятно это происходит потому,
#  что мы не контролируем содержимое первых 4 элементов
class StringScore:
	''' вьюв для Score, преедставленных в виде строки'''
	def __init__(self, score, config):
		self.score = score
		self.config = config

	def __str__(self):
		return self.score

	def json(self):
		''' Представление в виде json '''
		parts = self.score.split()
		return {
			'time': parts[0],
			'host': parts[1],
			'port': int(parts[2]),
			'invoice': parts[3],
			'suffixes': parts[4:],
			'strength': self.config['STRENGTH']
		}

	def prefix(self):
		''' Префиксная часть '''
		return ' '.join(self.score.split()[:4])

	def suffixes(self):
		''' Список суффиксов '''
		return self.score.split()[4:]


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
	def __init__(self, scores, config):
		self.scores = scores
		self.config = config

	def score(self):
		''' Фукнция возвращаем максимальный score '''
		return max(self.scores, key=lambda s: int(ScoreValue(s, self.config)))

	def __str__(self):
		return str(self.score())

	def json(self):
		''' В виде json '''
		return self.score().json()

	def prefix(self):
		''' Префиксная часть score '''
		return self.score().prefix()

	def suffixes(self):
		''' список суффиксов '''
		return self.score().suffixes()


class ValueScore:
	''' Score, который сопровождается значением Value '''
	def __init__(self, score, config):
		self.score = score
		self.config = config

	def json(self):
		''' Здесь к имеющимся полям добавляется метод value '''
		jscore = self.score.json()
		jscore['value'] = int(ScoreValue(JsonScore(jscore), self.config))
		return jscore


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

	def json(self):
		''' Новый core в виде json '''
		json = self.score.json()
		json['suffixes'].append(self.suffix)
		return json


class MinedScore:
	''' Score на один суффикс больше, чем предыдущее '''
	def __init__(self, score, config, seed=None):
		self.score = score
		self.config = config
		self.seed = seed if seed is not None else random.randint(
			0,
			0xffffffffffffffff
		)

	def prefix(self):
		''' Префикс такой же, как и у родительского score '''
		return self.score.prefix()

	def suffix_form(self, suffix_num):
		''' Строковое представление номера, сейчас это 7-значная строка в base58 '''
		return base58.b58encode(suffix_num.to_bytes(8, 'little'))[:7].decode('ascii')

	def new_suffix(self):
		''' Вычисление нового суффикса '''
		base = str(ScoreHash(self.score, self.config))
		return next((
			xs
			for xs in (
				self.suffix_form(s)
				for s in range(self.seed, 0xfffffffffffffffff)
			)
			if hashlib.sha256(
				(base + ' ' + xs).encode('ascii')
			).hexdigest().endswith('0' * self.config['STRENGTH'])
		))

	def suffixes(self):
		''' Суффиксы на один длиннее, чем были '''
		return self.score.suffixes() + [self.new_suffix()]

	def __str__(self):
		return str(self.score) + ' ' + self.new_suffix()

	def json(self):
		''' Новый core в виде json '''
		json = self.score.json()
		json['suffixes'].append(self.new_suffix())
		return json


class XZoldScore:
	''' Score, который используется в заголовке '''
	def __init__(self, score):
		self.xscore = score

	def score(self):
		''' Формируем строковую Score, и работаем через нее '''
		reg = re.match(r'\d+/(\d+): (.*)', self.xscore)
		return StringScore(reg.group(2), {'STRENGTH': reg.group(1)})

	def __str__(self):
		'''
		Не смотря на то, что X-Zold-Score имеет дополнительные поля,
		этот метод возвращает чистый Score в виде строки
		'''
		return str(self.score())

	def json(self):
		''' json достаем через StringScore '''
		return self.score().json()

	def prefix(self):
		''' Префикс достаем через StringScore '''
		return self.score().prefix()

	def suffixes(self):
		''' Суффиксы достаем через StringScore '''
		return self.score().suffixes()
