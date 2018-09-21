# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование Работы со списком задач '''

from test.zold.test_score import FakeScore
from flask_api import status
from node.app import APP
from node.db import DB, Score
from .test_wallet import FakeWallet, RootWallet, FullWallet


class WalletScore:
	''' Score для кошулька '''
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
			if t['type'] == 'find'
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
			if t['type'] == 'find'
		)

	def test_dst_wallet_to_wanted(self):
		''' Кошельки получатели помещаются в список tasks '''
		wallet = FullWallet(RootWallet(), 1000, APP.test_client())
		response = APP.test_client().get('/tasks')
		assert any(
			t['id'] == wallet.id() and t['prefix'] in wallet.public()
			for t in response.json['tasks']
			if t['type'] == 'wanted'
		)
