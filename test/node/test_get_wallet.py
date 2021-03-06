# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование Работы с кошельками '''

from test.zold.test_transaction import FakeTransaction
from test.zold.wallet import FakeWallet, RootWallet
from flask_api import status
from node.app import APP
from zold.wallet import TransactionWallet, WalletString
from .test_wallet import FullWallet


class TestGetWallet:
	''' Получение кошелька '''
	def test_wallet_not_found(self):
		''' Кошелек не найден на сервере '''
		response = APP.test_client().get('/wallet/dead3a11ed000000')
		assert response.status_code == status.HTTP_404_NOT_FOUND

	def test_wallet_ok(self):
		''' Сервер возвращает содержимое кошелька '''
		wallet = FakeWallet()
		APP.test_client().put(
			'/wallet/%s' % wallet.id(),
			data=str(WalletString(wallet))
		)
		response = APP.test_client().get('/wallet/%s' % wallet.id())
		assert response.status_code == status.HTTP_200_OK

	def test_incoming_transaction_bnf_is_sender(self):
		''' Идентификатор корневого должен фигурировать в транзакции получателя '''
		root_wallet = RootWallet()
		wallet = FullWallet(root_wallet, 1000, APP.test_client())
		APP.test_client().put(
			'/wallet/%s' % wallet.id(),
			data=str(WalletString(wallet))
		)
		response = APP.test_client().get('/wallet/%s' % wallet.id())
		assert root_wallet.id() in response.json['body']

	def test_incoming_transaction_approved(self):
		''' Входящая транзакций должна сразу появиться в кошельке получателе '''
		root_wallet = RootWallet()
		wallet = FakeWallet()
		transaction = FakeTransaction(root_wallet, wallet, -777)
		APP.test_client().put(
			'/wallet/%s' % wallet.id(),
			data=str(WalletString(wallet))
		)
		APP.test_client().put(
			'/wallet/%s' % root_wallet.id(),
			data=str(WalletString(TransactionWallet(root_wallet, transaction)))
		)
		response = APP.test_client().get('/wallet/%s' % wallet.id())
		assert root_wallet.id() in response.json['body']

	def test_wallet_mtime(self):
		''' В отзыве сервера присутствует время последней модификации кошелька '''
		root_wallet = RootWallet()
		wallet = FakeWallet()
		transaction = FakeTransaction(root_wallet, wallet, -555)
		APP.test_client().put(
			'/wallet/%s' % root_wallet.id(),
			data=str(WalletString(TransactionWallet(root_wallet, transaction)))
		)
		response = APP.test_client().get('/wallet/%s' % root_wallet.id())
		assert response.json['mtime'] == str(transaction.time())

	def test_wallet_balance(self):
		''' Запрос баланса по кошельку '''
		wallet = FullWallet(RootWallet(), 1000, APP.test_client())
		APP.test_client().put(
			'/wallet/%s' % wallet.id(),
			data=str(WalletString(
				TransactionWallet(wallet, FakeTransaction(wallet, FakeWallet(), -250))
			))
		)
		response = APP.test_client().get('/wallet/%s/balance' % wallet.id())
		assert response.data == b'750'
