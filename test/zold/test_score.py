# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Score '''

from datetime import datetime, timezone
from zold.score import JsonScore, MinedScore, StringScore, StrongestScore
from zold.scores import NewerThenScores, WeakScores
from zold.score_props import ScoreHash, ScoreValid, ScoreValue
from zold.time import DatetimeTime


# @todo #105 Необходимо иметь возможность создавать Score
#  с необходимыми параметрами и актуальной датой
class FakeScore:
	''' Тестовый score, он имеет необходимое количество суффиксов '''
	def __init__(self, value, config):
		if value > 0:
			self.score = MinedScore(
				FakeScore(value - 1, config),
				config,
				0
			)
		else:
			self.score = StringScore(
				'2018-06-20T20:01:32Z 127.0.0.1 4096 2X8kfnzk@9a856dac7d475014',
				config
			)

	def __str__(self):
		return str(self.score)

	def json(self):
		''' json представление '''
		return self.score.json()

	def prefix(self):
		''' Префиксная часть '''
		return self.score.prefix()

	def suffixes(self):
		''' Список суффиксов '''
		return self.score.suffixes()


class TestJsonScore:
	''' Тестирование JsonScore'''

	FULL = {
		'host': '185.180.196.2',
		'port': 4096,
		'invoice': '2X8kfnzk@9a856dac7d475014',
		'time': '2018-06-19T14:17:22Z',
		'suffixes': ['1e2434e', 'de5407', '14d43e4', '30a7d', '11afbbf', '4cd950']
	}

	EMPTY = {
		"host": "178.128.169.239",
		"port": 4096,
		"invoice": "Rg3XJle8@48b368ce23ed97fe",
		"time": "2018-06-20T20:01:32Z",
		"suffixes": []
	}

	def test_as_string(self):
		''' Проверяем, как JsonScore превращается в строку '''
		assert str(JsonScore(self.FULL)) == (
			'2018-06-19T14:17:22Z 185.180.196.2 4096 2X8kfnzk@9a856dac7d475014 '
			'1e2434e de5407 14d43e4 30a7d 11afbbf 4cd950'
		)

	def test_valid(self):
		''' Проверяем, что JsonScore валиден '''
		assert ScoreValid(JsonScore(self.FULL), {'STRENGTH': 6})

	def test_valid_empty(self):
		''' Проверяем, что JsonScore Без суффиксов тоже валиден '''
		assert ScoreValid(JsonScore(self.EMPTY), {'STRENGTH': 6})

	# @todo #50 ScoreValue должно тестироваться в отдельном классе,
	#  не нужно смешивать это с JsonScore
	def test_value(self):
		''' размер JsonScore '''
		assert int(ScoreValue(JsonScore(self.FULL), {'STRENGTH': 6})) == 6

	def test_value_empty(self):
		''' Размер пустого JsonScore '''
		assert int(ScoreValue(JsonScore(self.EMPTY), {'STRENGTH': 6})) == 0


class TestStrongestScore:
	''' Выбирает самый сильный Score из указанных '''
	STRONGEST = {
		'host': '185.180.196.2',
		'port': 4096,
		'invoice': '2X8kfnzk@9a856dac7d475014',
		'time': '2018-06-19T14:17:22Z',
		'suffixes': ['1e2434e', 'de5407', '14d43e4', '30a7d', '11afbbf', '4cd950']
	}

	EMPTY = {
		"host": "178.128.169.239",
		"port": 4096,
		"invoice": "Rg3XJle8@48b368ce23ed97fe",
		"time": "2018-06-20T20:01:32Z",
		"suffixes": []
	}

	def test_json(self):
		''' Тестируем выбор правильного core '''
		score = StrongestScore(
			[JsonScore(self.EMPTY), JsonScore(self.STRONGEST)],
			{'STRENGTH': 6}
		)
		assert score.json()['invoice'] == '2X8kfnzk@9a856dac7d475014'


class TestWeakScores:
	''' Тестирование списка Score, которые нуждаются в прокачке '''
	config = {'STRENGTH': 1}

	def test_empty(self):
		''' Проверка пустого списка '''
		assert not WeakScores([], 16, self.config)

	def test_weak(self):
		''' Проверка слабых score '''
		assert [
			int(ScoreValue(s, self.config))
			for s in WeakScores(
				[
					FakeScore(4, self.config),
					FakeScore(3, self.config),
					FakeScore(2, self.config),
					FakeScore(1, self.config),
					FakeScore(0, self.config)
				],
				3,
				self.config
			)
		] == [2, 1, 0]


class TestNewerThenScores:
	''' Тестирование списка Score, позднее указанной временнОй точки '''
	config = {'STRENGTH': 1}

	def test_newer(self):
		''' проверка фильтра '''
		score = StringScore(
			'2018-08-06T06:45:48Z 37.230.116.39 4096 HdssRDl6@cc53e22229564de6',
			self.config
		)
		assert len(NewerThenScores(
			[score],
			DatetimeTime(datetime(2018, 8, 6, 6, 45, 45, tzinfo=timezone.utc))
		)) == 1
		assert list(NewerThenScores(
			[score],
			DatetimeTime(datetime(2018, 8, 6, 6, 45, 54, tzinfo=timezone.utc))
		))


class TestScoreHash:
	''' Тесты на ScoreHash '''
	FULL = {
		'host': '185.180.196.2',
		'port': 4096,
		'invoice': '2X8kfnzk@9a856dac7d475014',
		'time': '2018-06-19T14:17:22Z',
		'suffixes': ['1e2434e', 'de5407', '14d43e4', '30a7d', '11afbbf', '4cd950']
	}

	EMPTY = {
		'host': '178.128.169.239',
		'port': 4096,
		'invoice': 'Rg3XJle8@48b368ce23ed97fe',
		'time': '2018-06-20T20:01:32Z',
		'suffixes': []
	}

	def test_empty_hash(self):
		''' Тест на хеш пустого Score, а хеш у него - префиксная часть '''
		assert str(ScoreHash(JsonScore(self.EMPTY), {'STRENGTH': 6})) == (
			'2018-06-20T20:01:32Z 178.128.169.239 4096 Rg3XJle8@48b368ce23ed97fe'
		)

	def test_full_hash(self):
		''' Тест ха хеш полного score'''
		assert str(ScoreHash(JsonScore(self.FULL), {'STRENGTH': 6})) == (
			'b7948e996c6765c1d625dafbb6d3aa5fabddc7232cdec19430c8d0960e000000'
		)
