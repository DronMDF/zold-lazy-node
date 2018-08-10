# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование ScoreProps '''
from zold.score import JsonScore
from zold.score_props import ScoreHash, ScoreValue


class TestScoreValue:
	''' Тестирование ScoreValue '''
	FULL = {
		"time": "2018-08-10T05:26:30Z",
		"host": "b2.zold.io",
		"port": 4096,
		"invoice": "RJppWlJD@912ecc24b32dbe74",
		"suffixes": [
			"176d9", "2e8269", "190ac32", "1a9cbe", "f76287",
			"69c473", "9ec1ac", "1cf1c66", "9b37e2", "6af3c5",
			"e670a8", "1594076", "1c2495e", "17efeb", "d02de",
			"743914", "2e987b3", "6cb6cf", "4ac859", "3aea17",
			"1ce3b16"
		]
	}

	EMPTY = {
		"time": "2018-08-10T21:00:45Z",
		"host": "b1.zold.io",
		"port": 80,
		"invoice": "ML5Ern7m@912ecc24b32dbe74",
		"suffixes": []
	}

	def test_value(self):
		''' размер JsonScore '''
		assert int(ScoreValue(JsonScore(self.FULL), {'STRENGTH': 6})) == 21

	def test_value_empty(self):
		''' Размер пустого JsonScore '''
		assert int(ScoreValue(JsonScore(self.EMPTY), {'STRENGTH': 6})) == 0


class TestScoreHash:
	''' Тесты на ScoreHash '''
	FULL = {
		'time': '2018-06-19T14:17:22Z',
		'host': '185.180.196.2',
		'port': 4096,
		'invoice': '2X8kfnzk@9a856dac7d475014',
		'suffixes': ['1e2434e', 'de5407', '14d43e4', '30a7d', '11afbbf', '4cd950']
	}

	EMPTY = {
		'time': '2018-06-20T20:01:32Z',
		'host': '178.128.169.239',
		'port': 4096,
		'invoice': 'Rg3XJle8@48b368ce23ed97fe',
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
