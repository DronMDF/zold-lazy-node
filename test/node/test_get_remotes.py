# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование Работы с кошельками '''

from flask_api import status
from node.app import APP


class TestGetRemotes:
	''' Тестирование GET /remotes '''
	def test_score_in_reply(self):
		''' Сервер в ответе возвращает свой текущий score '''
		response = APP.test_client().get('/remotes')
		assert response.status_code == status.HTTP_200_OK
		assert 'score' in response.json
