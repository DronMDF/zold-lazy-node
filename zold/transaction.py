# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Работа с транзакциями '''

from .time import StringTime


class StringTransaction:
	''' Транзакция, представленная в виде строки'''
	def __init__(self, transaction):
		self.transaction = transaction

	def id(self):
		''' Идентификатор транзакции '''
		return int(self.transaction.split(';')[0], 16)

	def time(self):
		''' Время транзакции '''
		return StringTime(self.transaction.split(';')[1])

	def amount(self):
		''' Сумма транзакции в zent'ах '''
		amount = int(self.transaction.split(';')[2], 16)
		if amount < 0x8000000000000000:
			return amount
		return amount - 0x10000000000000000

	def prefix(self):
		''' префикс '''
		return self.transaction.split(';')[3]

	def bnf(self):
		''' Соучастник транзакции '''
		return self.transaction.split(';')[4]

	def details(self):
		''' описание '''
		return self.transaction.split(';')[5]

	def signature(self):
		''' сигнатура '''
		return self.transaction.split(';')[6]


class IncomingTransaction:
	''' Входящая транзакция '''
	def __init__(self, transaction):
		self.transaction = transaction

	def amount(self):
		''' Транзакция имеет положительное значение '''
		return -self.transaction.amount()

	def signature(self):
		''' Сигнатура пуста '''
		return ''

	def __getattr__(self, attr):
		return self.transaction.__getattr__(attr)


class IncomingTransactions:
	''' Входящие транзакции '''
	def __init__(self, transactions):
		self.transactions = transactions

	def __iter__(self):
		return (IncomingTransaction(t) for t in self.transactions)


class OrderedTransactions:
	''' Список транзакций, упорядоченный по времени '''
	def __init__(self, transactions):
		self.transactions = transactions

	def __iter__(self):
		return iter(sorted(self.transactions, key=lambda t: t.time().as_datetime()))


class TransactionString:
	''' Транзакция в виде строки '''
	def __init__(self, transaction):
		self.transaction = transaction

	def __str__(self):
		transaction_id = '%04x' % self.transaction.id()
		time = str(self.transaction.time())
		if self.transaction.amount() < 0:
			amount = '%016x' % (self.transaction.amount() + 0x10000000000000000)
		else:
			amount = '%016x' % self.transaction.amount()
		prefix = self.transaction.prefix()
		bnf = self.transaction.bnf()
		details = self.transaction.details()
		signature = self.transaction.signature()
		return ';'.join((
			transaction_id,
			time,
			amount,
			prefix,
			bnf,
			details,
			signature
		))
