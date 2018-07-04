# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование майнинга '''

import hashlib
from flask_api import status
from node.app import APP
from zold.score import JsonScore, ScoreHash


class TestPutScore:
	''' Тестируем точку входа  PUT /score'''
	def test_wrong_suffix(self):
		''' Если суффикс никуда не подходит - клиент получает 406 '''
		response = APP.test_client().post('/score', json={'suffix': 'bad'})
		assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE

	def test_right_suffix(self):
		'''
		Правильный суффикс принимается сервером и включается в отдачу
		Чтобы тест не зависео от времени - он должен сам майнить...
		это медленно, поэтому мы проверяем здесь и тот факт, что сервер
		зафиксировал у себя результат нашей работы.
		'''
		info = APP.test_client().get('/')
		score = JsonScore(info.json.get('score'))
		prefix = str(ScoreHash(score))
		suffix = next((
			xs
			for xs in (hex(s) for s in range(0xffffffffffffffff))
			if hashlib.sha256(
				(prefix + ' ' + xs).encode('ascii')
			).hexdigest().endswith('0' * 6)
		))
		response = APP.test_client().post('/score', json={'suffix': suffix})
		assert response.status_code == status.HTTP_200_OK
		assert suffix in JsonScore(
			APP.test_client().get('/').json.get('score')
		).suffixes()
