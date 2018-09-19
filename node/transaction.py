# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Работа с транзакциями '''

from node.db import Transaction
from zold.time import DatetimeTime


class DbTransaction:
	''' Одна транзакция из БД '''
	def __init__(self, transaction):
		self.transaction = transaction

	def id(self):
		''' Идентификатор транзакции '''
		return self.transaction.transaction_id

	def time(self):
		''' Время транзакции '''
		return DatetimeTime(self.transaction.time)

	def amount(self):
		''' сумма транзакции '''
		return self.transaction.amount

	def prefix(self):
		''' префикс '''
		return self.transaction.dst_prefix

	def bnf(self):
		''' соучастник '''
		return self.transaction.dst_id

	def details(self):
		''' описание '''
		return self.transaction.details

	def signature(self):
		''' сигнатура '''
		return self.transaction.signature


class DbTransactions:
	''' Коллекция транзакций в БД '''
	def select(self, **query):
		''' Выбор транзакций из БД '''
		return (DbTransaction(t) for t in Transaction.query.filter_by(**query).all())
