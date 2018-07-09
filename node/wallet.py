# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Работа с кошельками '''

from node.db import DB, Wallet


class DbWallet:
	''' Представление кошелька '''
	def __init__(self, wallet_id, body=None):
		self.wallet_id = wallet_id
		self.text = body

	def body(self):
		''' Чтение содержимого кошелька '''
		dbwallet = Wallet.query.filter_by(wallet_id=self.wallet_id).first()
		if dbwallet is None:
			raise RuntimeError('Wallet not found')
		return dbwallet.body

	def save(self):
		''' Обновление содержимого кошелька '''
		dbwallet = Wallet.query.filter_by(wallet_id=self.wallet_id).first()
		if dbwallet is not None:
			dbwallet.body = self.text
		else:
			DB.session.add(Wallet(self.wallet_id, self.text))
		DB.session.commit()
