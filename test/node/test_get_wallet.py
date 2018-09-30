# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование Работы с кошельками '''

from test.zold.test_transaction import FakeTransaction
from flask_api import status
from node.app import APP
from zold.wallet import TransactionWallet
from .test_wallet import FakeWallet, FullWallet, RootWallet


class TestGetWallet:
	''' Получение кошелька '''
	def test_wallet_not_found(self):
		''' Кошелек не найден на сервере '''
		response = APP.test_client().get('/wallet/dead3a11ed000000')
		assert response.status_code == status.HTTP_404_NOT_FOUND

	def test_wallet_ok(self):
		''' Сервер возвращает содержимое кошелька '''
		wallet = FakeWallet()
		APP.test_client().put('/wallet/%s' % wallet.id(), data=str(wallet))
		response = APP.test_client().get('/wallet/%s' % wallet.id())
		assert response.status_code == status.HTTP_200_OK

	def test_incoming_transaction_bnf_is_sender(self):
		''' Идентификатор корневого должен фигурировать в транзакции получателя '''
		root_wallet = RootWallet()
		wallet = FullWallet(root_wallet, 1000, APP.test_client())
		APP.test_client().put('/wallet/%s' % wallet.id(), data=str(wallet))
		response = APP.test_client().get('/wallet/%s' % wallet.id())
		assert root_wallet.id() in response.json['body']

	def test_incoming_transaction_approved(self):
		''' Входящая транзакций должна сразу появиться в кошельке получателе '''
		root_wallet = RootWallet()
		wallet = FakeWallet()
		transaction = FakeTransaction(root_wallet, wallet, -777)
		APP.test_client().put('/wallet/%s' % wallet.id(), data=str(wallet))
		APP.test_client().put(
			'/wallet/%s' % root_wallet.id(),
			data=str(TransactionWallet(root_wallet, transaction))
		)
		response = APP.test_client().get('/wallet/%s' % wallet.id())
		assert root_wallet.id() in response.json['body']
