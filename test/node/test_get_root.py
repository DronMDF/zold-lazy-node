# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование корневого урла '''

from test.zold.test_score import FakeScore
from node.app import APP
from zold.score_props import ScoreValue


class TestGetRoot:
	''' Тестирование содержимого корневой страницы '''

	def test_x_zold_version(self):
		''' Заголовок должен содержать X-Zold-Version '''
		response = APP.test_client().get('/')
		assert 'X-Zold-Version' in response.headers

	def test_body_contents(self):
		''' Тело реплая должно содержать определенные поля '''
		json = APP.test_client().get('/').json
		assert 'cpus' in json
		assert 'hours_alive' in json
		assert 'load' in json
		assert 'memory' in json
		assert 'nscore' in json
		assert 'platform' in json
		assert 'protocol' in json
		assert 'remotes' in json
		assert 'threads' in json
		assert 'version' in json
		assert 'wallets' in json
		assert 'value' in json['score']
		assert 'history_size' in json['entrance']
		assert 'queue_age' in json['entrance']
		assert 'queue' in json['entrance']
		assert 'speed' in json['entrance']

	def test_remote_from_header_scores(self):
		'''
		Тестируем, как сервер принимает информацию о новых ремотах
		через содержимое заголовка
		'''
		config = {'STRENGTH': 3}
		score = FakeScore(3, config)
		APP.test_client().get(
			'/',
			headers={
				'X-Zold-Score': '%u/%u: %s' % (ScoreValue(score, config), 3, score)
			}
		)
		response = APP.test_client().get('/remotes')
		assert any((
			r['host'] == '127.0.0.1' and r['port'] == 4096
			for r in response.json['all']
		))
