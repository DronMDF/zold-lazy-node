# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Score '''

from zold.score import (
	JsonScore,
	ScoreHash,
	ScoreValid,
	ScoreValue,
	StrongestScore
)


class TestJsonScore:
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

	''' JsonScore тесты '''
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
		assert ScoreValue(JsonScore(self.FULL), {'STRENGTH': 6}).value() == 6

	def test_value_empty(self):
		''' Размер пустого JsonScore '''
		assert ScoreValue(JsonScore(self.EMPTY), {'STRENGTH': 6}).value() == 0


class TestStrongestScore:
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
		score = StrongestScore(
			[JsonScore(self.EMPTY), JsonScore(self.STRONGEST)],
			{'STRENGTH': 6}
		)
		assert score.json()['invoice'] == '2X8kfnzk@9a856dac7d475014'


class TestScoreHash:
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
		assert str(ScoreHash(JsonScore(self.EMPTY), {'STRENGTH': 6})) == (
			'2018-06-20T20:01:32Z 178.128.169.239 4096 Rg3XJle8@48b368ce23ed97fe'
		)

	def test_full_hash(self):
		assert str(ScoreHash(JsonScore(self.FULL), {'STRENGTH': 6})) == (
			'b7948e996c6765c1d625dafbb6d3aa5fabddc7232cdec19430c8d0960e000000'
		)
