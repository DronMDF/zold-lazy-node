# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование корневого урла '''

from test.zold.test_score import FakeScore
from node.app import APP


class TestGetRoot:
	''' Тестирование содержимого корневой страницы '''

	def test_x_zold_version(self):
		''' Заголовок должен содержать X-Zold-Version '''
		response = APP.test_client().get('/')
		assert 'X-Zold-Version' in response.headers

	def test_remote_from_header_scores(self):
		'''
		Тестируем, как сервер принимает информацию о новых ремотах
		через содержимое заголовка
		'''
		APP.test_client().get(
			'/',
			headers={'X-Zold-Score': str(FakeScore(3, {'STRENGTH': 3}))}
		)
		response = APP.test_client().get('/remotes')
		print(response.json)
		assert any((
			r['host'] == '127.0.0.1' and r['port'] == 4096
			for r in response.json['all']
		))
