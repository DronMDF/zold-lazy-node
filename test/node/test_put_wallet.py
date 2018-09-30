# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование Работы с кошельками '''

from test.zold.test_transaction import FakeTransaction
from flask_api import status
from node.app import APP
from zold.score import JsonScore
from zold.score_props import ScoreValid
from zold.wallet import TransactionWallet
from zold.transaction import TransactionString
from .test_wallet import FakeWallet, RootWallet


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

	def test_put_root_wallet_import_all_valid(self):
		'''
		Загрузка корневого кошелька
		На нем не бывает нехватки средств
		И все транзакции необходимо проверять и принимать
		'''
		src_wallet = RootWallet()
		dst_wallet = FakeWallet()
		transact = FakeTransaction(src_wallet, dst_wallet, -1000)
		wallet = TransactionWallet(src_wallet, transact)
		APP.test_client().put('/wallet/%s' % wallet.id(), data=str(wallet))
		response = APP.test_client().get('/wallet/%s' % wallet.id())
		assert response.status_code == status.HTTP_200_OK
		# Там могут быть левые транзакции, поэтому ищем нашу
		assert str(TransactionString(transact)) in response.json['body']

	def test_put_wallet_negative_balance(self):
		'''
		Загрузка кошелька с негативным балансом - не ошибка
		но избыточные транзакции не проверяем и не сохраняем
		'''
		src_wallet = FakeWallet()
		dst_wallet = FakeWallet()
		transact = FakeTransaction(src_wallet, dst_wallet, -1000)
		wallet = TransactionWallet(src_wallet, transact)
		APP.test_client().put('/wallet/%s' % wallet.id(), data=str(wallet))
		response = APP.test_client().get('/wallet/%s' % wallet.id())
		assert response.status_code == status.HTTP_200_OK
		# Транзакция не возвращается, поскольку не прошла проверку.
		assert response.json['body'] == str(src_wallet)

	def test_put_wallet_negative_balance_partial(self):
		'''
		Загрузка кошелька с негативным балансом - не ошибка
		но избыточные транзакции не проверяем и не сохраняем
		Но хорошие принимаем
		'''
		root_wallet = RootWallet()
		src_wallet = FakeWallet()
		APP.test_client().put(
			'/wallet/%s' % root_wallet.id(),
			data=str(TransactionWallet(
				root_wallet,
				FakeTransaction(root_wallet, src_wallet, -1500)
			))
		)
		dst_wallet = FakeWallet()
		transaction1 = FakeTransaction(src_wallet, dst_wallet, -1000)
		transaction2 = FakeTransaction(src_wallet, dst_wallet, -600)
		APP.test_client().put(
			'/wallet/%s' % src_wallet.id(),
			data=str(TransactionWallet(src_wallet, transaction1, transaction2))
		)
		response = APP.test_client().get('/wallet/%s' % src_wallet.id())
		assert response.status_code == status.HTTP_200_OK
		assert str(TransactionString(transaction1)) in response.json['body']
		# Вторая транзакция не должна проходить
		assert str(TransactionString(transaction2)) not in response.json['body']
