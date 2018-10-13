# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестовые транзакции '''


class IncomingTransaction:
	''' Входящая транзакция '''
	def __init__(self, wallet, transaction):
		self.wallet = wallet
		self.transaction = transaction

	def amount(self):
		''' Баланс '''
		return -self.transaction.amount()

	def bnf(self):
		''' Отправитель '''
		return self.wallet.id()

	def signature(self):
		''' Сигнатуры нет '''
		return ''

	def __getattr__(self, attr):
		return getattr(self.transaction, attr)
