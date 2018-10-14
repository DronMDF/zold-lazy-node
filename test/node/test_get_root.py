# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование корневого урла '''

from test.zold.test_score import FakeScore
from test.zold.wallet import RootWallet
from node.app import APP
from node.db import DB, Remote
from zold.wallet import WalletString
from .test_wallet import FullWallet


class TestGetRoot:
	''' Тестирование содержимого корневой страницы '''

	def test_reply_header(self):
		''' Заголовок должен содержать определенный набор полей '''
		response = APP.test_client().get('/')
		assert response.headers['Access-Control-Allow-Origin'] == '*'
		assert 'X-Zold-Version' in response.headers

	def test_body_contents(self):
		''' Тело реплая должно содержать определенные поля '''
		json = APP.test_client().get('/').json
		assert 'cpus' in json
		assert 'hours_alive' in json
		assert 'load' in json
		assert 'memory' in json
		assert 'nscore' in json
		assert 'platform' in json
		assert 'protocol' in json
		assert 'remotes' in json
		assert 'threads' in json
		assert 'version' in json
		assert 'wallets' in json
		assert 'value' in json['score']
		assert 'history_size' in json['entrance']
		assert 'queue_age' in json['entrance']
		assert 'queue' in json['entrance']
		assert 'speed' in json['entrance']

	def test_remote_from_header_scores(self):
		'''
		Тестируем, как сервер принимает информацию о новых ремотах
		через содержимое заголовка
		'''
		with APP.app_context():
			DB.session.query(Remote).delete()
		APP.test_client().get(
			'/',
			headers={
				'X-Zold-Score': '3/3: %s' % FakeScore(
					3,
					{'STRENGTH': 3},
					host='5.4.3.2',
					port=2048
				)
			}
		)
		response = APP.test_client().get('/remotes')
		assert any((
			r['host'] == '5.4.3.2' and r['port'] == 2048
			for r in response.json['all']
		))

	def test_wallet_count(self):
		''' Количество кошельков меняется, как минимум не равно 1 '''
		wallet = FullWallet(RootWallet(), 666, APP.test_client())
		APP.test_client().put(
			'/wallet/%s' % wallet.id(),
			data=str(WalletString(wallet))
		)
		response = APP.test_client().get('/')
		assert response.json['wallets'] >= 2
