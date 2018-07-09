# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование Работы с кошельками '''

from flask_api import status
from node.app import APP


class TestGetWallet:
	''' Получение кошелька '''
	def test_wallet_not_found(self):
		''' Кошелек не найден на сервере '''
		response = APP.test_client().get('/wallet/dead3a11ed000000')
		assert response.status_code == status.HTTP_404_NOT_FOUND
