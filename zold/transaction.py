# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Работа с транзакциями '''

import base64
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
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
		return getattr(self.transaction, attr)


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


class OutgoingTransactions:
	''' Список исходящих транзакций '''
	def __init__(self, transactions):
		self.transactions = transactions

	def __iter__(self):
		return (t for t in self.transactions if t.amount() < 0)


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


class TransactionValid:
	''' Состояние транзакции '''
	def __init__(self, transaction, wallet):
		self.transaction = transaction
		self.wallet = wallet

	def __bool__(self):
		# @todo #163 Формирование данных транзакции для подписи - типовая операция.
		#  Повторяется например еще в test.node.test_wallet.FakeTransaction
		transaction_id = '%04x' % self.transaction.id()
		time = str(self.transaction.time())
		amount = self.transaction.amount()
		if amount < 0:
			amount += 0x10000000000000000
		amstr = '%016x' % amount
		prefix = self.transaction.prefix()
		bnf = self.transaction.bnf()
		details = self.transaction.details()
		key = RSA.importKey(base64.b64decode(self.wallet.public()))
		return PKCS1_v1_5.new(key).verify(SHA256.new(' '.join(
			(bnf, transaction_id, time, amstr, prefix, bnf, details)
		).encode('ascii')), base64.b64decode(self.transaction.signature()))


class TransactionsAmount:
	''' Общая сумма транзакций '''
	def __init__(self, transactions):
		self.transactions = transactions

	def __int__(self):
		return sum((t.amount() for t in self.transactions))
