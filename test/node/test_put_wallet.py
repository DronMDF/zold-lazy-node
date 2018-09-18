# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование Работы с кошельками '''

from flask_api import status
from node.app import APP
from zold.score import JsonScore
from zold.score_props import ScoreValid
from .test_wallet import FakeWallet


class TestPutWallet:
	''' Тестируем PUT /wallet/<id> '''
	def test_return_score(self):
		''' В ответе сервер указывает свой score '''
		wallet = FakeWallet()
		response = APP.test_client().put(
			'/wallet/%s' % wallet.id(),
			data=str(wallet)
		)
		assert ScoreValid(JsonScore(response.json['score']), APP.config)

	def test_put_wallet_again(self):
		''' Повторная загрузка кошелька не должна приводить к ошибке '''
		wallet = FakeWallet()
		APP.test_client().put('/wallet/%s' % wallet.id(), data=str(wallet))
		response = APP.test_client().put(
			'/wallet/%s' % wallet.id(),
			data=str(wallet)
		)
		assert response.status_code == status.HTTP_200_OK
