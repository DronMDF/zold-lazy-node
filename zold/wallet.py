# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.


'''
Кошельки
'''

from .transaction import StringTransaction, TransactionString


class StringWallet:
	''' Кошелек, представленный в виде строки '''
	def __init__(self, wallet):
		self.wallet = wallet

	def id(self):
		''' Идентификатор кошелька '''
		return self.wallet.split('\n')[2]

	def network(self):
		''' Название сети '''
		return self.wallet.split('\n')[0]

	def public(self):
		''' Публичный ключ '''
		return self.wallet.split('\n')[3]

	def transactions(self):
		''' Список транзакций '''
		return (StringTransaction(t) for t in self.wallet.split('\n')[5:])


class TransactionWallet:
	''' Декоратор для кошелька - добавляет транзакции '''
	def __init__(self, wallet, *transactions):
		self.wallet = wallet
		self.transactions = transactions

	def id(self):
		''' Идентификатор кошелька '''
		return self.wallet.id()

	def __str__(self):
		return '\n'.join((
			str(self.wallet),
			*[str(TransactionString(t)) for t in self.transactions]
		))
