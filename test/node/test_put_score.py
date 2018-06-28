# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование майнинга '''

from flask_api import status
from node.app import APP


class TestPutScore:
	''' Тестируем точку входа  PUT /score'''
	def test_wrong_suffix(self):
		''' Если суффикс никуда не подходит - клиент получает 406 '''
		response = APP.test_client().post('/score', json={'suffix': 'bad'})
		assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
