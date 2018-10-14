# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование кошельков (пока здесь только тестовый кошелек) '''

from test.zold.test_transaction import FakeTransaction
from test.zold.wallet import FakeWallet
from zold.wallet import TransactionWallet


class FullWallet:
	'''
	Кошелек с балансом
	Кошелек не публикуется на сервер, для разных сценариев
	Если проверяется содержимое с сервера - его надо опубликовать.
	'''
	def __init__(self, sponsor, amount, client):
		self.wallet = FakeWallet()
		client.put(
			'/wallet/%s' % sponsor.id(),
			data=str(TransactionWallet(
				sponsor,
				FakeTransaction(sponsor, self.wallet, -amount)
			))
		)

	def __getattr__(self, attr):
		return getattr(self.wallet, attr)

	def __str__(self):
		return str(self.wallet)
