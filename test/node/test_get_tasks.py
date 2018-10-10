# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование Работы со списком задач '''

from test.zold.test_score import FakeScore
from test.zold.test_transaction import BadPrefixTransaction, FakeTransaction
from flask_api import status
from node.app import APP
from node.db import DB, Score
from zold.wallet import TransactionWallet
from zold.transaction import TransactionString
from .test_wallet import FakeWallet, RootWallet, FullWallet
from .test_transaction import IncomingTransaction


class WalletScore:
	''' Score для кошeлька '''
	def __init__(self, wallet):
		self.wallet = wallet

	def __str__(self):
		return str(
			FakeScore(
				3,
				APP.config,
				prefix=self.wallet.prefix(),
				id=self.wallet.id()
			)
		)


class TestGetTasks:
	''' Тестирование GET /tasks'''
	def test_mining_tasks(self):
		''' В списке задач присутствуют задачи майнинга '''
		with APP.app_context():
			DB.session.query(Score).delete()
		response = APP.test_client().get('/tasks')
		assert response.status_code == status.HTTP_200_OK
		assert any(t['type'] == 'mining' for t in response.json['tasks'])

	def test_remotes_tasks(self):
		''' В списке задач присутствуют задачи поиска кошелька '''
		wallet = FakeWallet()
		APP.test_client().get(
			'/',
			headers={'X-Zold-Score': '3/3: %s' % WalletScore(wallet)}
		)
		response = APP.test_client().get('/tasks')
		assert response.status_code == status.HTTP_200_OK
		assert any(
			t['id'] == wallet.id() and t['prefix'] in wallet.public()
			for t in response.json['tasks']
			if t['type'] == 'wanted'
		)

	def test_remotes_not_need_tasks(self):
		''' В списке задач отсутствую задачи поиска, если кошелек присутствует '''
		wallet = FakeWallet()
		APP.test_client().get(
			'/',
			headers={'X-Zold-Score': '3/3: %s' % WalletScore(wallet)}
		)
		APP.test_client().put('/wallet/%s' % wallet.id(), data=str(wallet))
		response = APP.test_client().get('/tasks')
		assert response.status_code == status.HTTP_200_OK
		assert not any(
			t['id'] == wallet.id()
			for t in response.json['tasks']
			if t['type'] == 'wanted'
		)

	def test_dst_wallet_to_wanted(self):
		''' Кошельки получатели помещаются в список tasks '''
		root = RootWallet()
		wallet = FullWallet(root, 1000, APP.test_client())
		response = APP.test_client().get('/tasks')
		assert any(
			all((
				t['id'] == wallet.id(),
				t['prefix'] in wallet.public(),
				t.get('who', None) == root.id()
			))
			for t in response.json['tasks']
			if t['type'] == 'wanted'
		)

	def test_dst_wallet_from_wanted(self):
		''' Кошельки получатели удаляются из списка tasks '''
		wallet = FullWallet(RootWallet(), 1000, APP.test_client())
		APP.test_client().put('/wallet/%s' % wallet.id(), data=str(wallet))
		response = APP.test_client().get('/tasks')
		assert not any(
			t['id'] == wallet.id()
			for t in response.json['tasks']
			if t['type'] == 'wanted'
		)

	def test_dst_wallet_from_wanted_if_not_match(self):
		'''
		Кошельки получатели удаляются из списка tasks,
		даже если не совпадает префикс
		'''
		src = FullWallet(RootWallet(), 1000, APP.test_client())
		dst = FakeWallet()
		transaction = BadPrefixTransaction(src, dst, -100)
		APP.test_client().put(
			'/wallet/%s' % src.id(),
			data=str(TransactionWallet(src, transaction))
		)
		APP.test_client().put('/wallet/%s' % dst.id(), data=str(dst))
		response = APP.test_client().get('/tasks')
		assert not any(
			t['id'] in [src.id(), dst.id()]
			for t in response.json['tasks']
			if t['type'] == 'wanted'
		)

	def test_src_wallet_to_wanted(self):
		''' Кошельки отправители помещаются в список tasks '''
		src = FakeWallet()
		dst = FakeWallet()
		APP.test_client().put(
			'/wallet/%s' % dst.id(),
			data=str(TransactionWallet(
				dst,
				IncomingTransaction(src, FakeTransaction(src, dst, -1500))
			))
		)
		response = APP.test_client().get('/tasks')
		assert any(
			t['id'] == src.id() and t.get('who', None) == dst.id()
			for t in response.json['tasks']
			if t['type'] == 'wanted'
		)

	def test_src_wallet_wanted_once(self):
		'''
		Известные отправители отправители помещаются в список tasks
		только один раз
		'''
		src = FakeWallet()
		dst = FakeWallet()
		transaction = FakeTransaction(src, dst, -777)
		APP.test_client().put(
			'/wallet/%s' % dst.id(),
			data=str(TransactionWallet(dst, IncomingTransaction(src, transaction)))
		)
		APP.test_client().put(
			'/wallet/%s' % dst.id(),
			data=str(TransactionWallet(dst, IncomingTransaction(src, transaction)))
		)
		response = APP.test_client().get('/tasks')
		assert len([
			t
			for t in response.json['tasks']
			if t['type'] == 'wanted' and t['id'] == src.id()
		]) == 1

	def test_known_src_wallet_not_wanted(self):
		''' Известные отправители отправители не помещаются в список tasks '''
		src_wallet = FullWallet(RootWallet(), 1000, APP.test_client())
		wallet = FakeWallet()
		dst_wallet = FakeWallet()
		src_transaction = FakeTransaction(src_wallet, dst_wallet, -777)
		transaction = FakeTransaction(wallet, dst_wallet, -1500)
		APP.test_client().put(
			'/wallet/%s' % src_wallet.id(),
			data=str(TransactionWallet(src_wallet, src_transaction))
		)
		APP.test_client().put(
			'/wallet/%s' % dst_wallet.id(),
			data=str(TransactionWallet(
				dst_wallet,
				IncomingTransaction(src_wallet, src_transaction),
				IncomingTransaction(wallet, transaction),
			))
		)
		response = APP.test_client().get('/tasks')
		assert not any(
			t['id'] == src_wallet.id()
			for t in response.json['tasks']
			if t['type'] == 'wanted'
		)

	def test_src_wallet_from_wanted_trivial(self):
		''' Кошелек убирается из поиска, простой случай '''
		src = FullWallet(RootWallet(), 3000, APP.test_client())
		dst = FakeWallet()
		transaction = FakeTransaction(src, dst, -777)
		APP.test_client().put(
			'/wallet/%s' % dst.id(),
			data=str(TransactionWallet(
				dst,
				IncomingTransaction(src, transaction)
			))
		)
		APP.test_client().put(
			'/wallet/%s' % src.id(),
			data=str(TransactionWallet(src, transaction))
		)
		response = APP.test_client().get('/tasks')
		assert not any(
			t['id'] == src.id()
			for t in response.json['tasks']
			if t['type'] == 'wanted'
		)

	def test_src_wallet_from_wanted(self):
		''' В случае поступления транзакции, запись убирается из поиск '''
		src = FullWallet(RootWallet(), 3000, APP.test_client())
		dst = FakeWallet()
		transaction1 = FakeTransaction(src, dst, -777)
		transaction2 = FakeTransaction(src, dst, -1500)
		APP.test_client().put(
			'/wallet/%s' % dst.id(),
			data=str(TransactionWallet(
				dst,
				IncomingTransaction(src, transaction1),
				IncomingTransaction(src, transaction2),
			))
		)
		APP.test_client().put(
			'/wallet/%s' % src.id(),
			data=str(TransactionWallet(src, transaction2))
		)
		response = APP.test_client().get('/tasks')
		assert any(
			all((
				t['id'] == src.id(),
				t.get('who', None) == dst.id(),
				t['transaction'] == str(
					TransactionString(IncomingTransaction(src, transaction1))
				)
			))
			for t in response.json['tasks']
			if t['type'] == 'wanted'
		)
		assert not any(
			all((
				t['id'] == src.id(),
				t['transaction'] == str(
					TransactionString(IncomingTransaction(src, transaction2))
				)
			))
			for t in response.json['tasks']
			if t['type'] == 'wanted'
		)
