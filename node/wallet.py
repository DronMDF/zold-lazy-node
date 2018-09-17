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
		wallet = Wallet.query.filter_by(wallet_id=self.wallet_id).first()
		if wallet is None:
			raise RuntimeError('Wallet not found')
		return '\n'.join((wallet.network, '2', self.wallet_id, wallet.public, ''))

	def save(self):
		''' Обновление содержимого кошелька '''
		dbwallet = Wallet.query.filter_by(wallet_id=self.wallet_id).first()
		if dbwallet is not None:
			dbwallet.body = self.text
		else:
			DB.session.add(Wallet(self.wallet_id, self.text))
		DB.session.commit()


# @todo #139 DbWallet должен представлять структуру БД, но это имя занято
class DbRecordWallet:
	''' Одиночный кошелек в БД'''
	def __init__(self, wallet):
		self.wallet = wallet

	# @todo #139 Название метода id считается невалидным,
	#  хотя оно подходит больше всего. Kак же назвать этот метод?
	def wid(self):
		''' Идентификатор кошелька '''
		return self.wallet.wallet_id


class DbWallets:
	''' Все кошельки в БД '''
	def __iter__(self):
		return (DbRecordWallet(w) for w in Wallet.query.all())
