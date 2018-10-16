# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Работа с транзакциями '''

from node.db import DB, Transaction, TransactionDstStatus
from zold.time import DatetimeTime
from zold.transaction import (
	OrderedTransactions,
	OutgoingTransactions,
	TransactionIn,
	TransactionValid
)


class DbTransaction:
	''' Одна транзакция из БД '''
	def __init__(self, transaction):
		self.transaction = transaction

	def dbref(self):
		''' Идентификатор БД для обновления записей '''
		return self.transaction.id

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
		''' получатель платежа '''
		return self.transaction.dst_id

	def details(self):
		''' описание '''
		return self.transaction.details

	def signature(self):
		''' сигнатура '''
		return self.transaction.signature

	def src(self):
		''' Отправитель платежа, дополнительное API '''
		return self.transaction.src_id

	def update(self, status):
		''' Обновление состояния транзакции '''
		self.transaction.dst_status = status
		DB.session.commit()


class IncomingDbTransaction:
	''' Одна транзакция из БД '''
	def __init__(self, transaction):
		self.src_id = transaction.src_id
		self.transaction = DbTransaction(transaction)

	def amount(self):
		''' сумма транзакции '''
		return -self.transaction.amount()

	def bnf(self):
		''' соучастник '''
		return self.src_id

	def signature(self):
		''' сигнатура '''
		return ''

	def __getattr__(self, attr):
		return getattr(self.transaction, attr)


class DbTransactions:
	''' Коллекция транзакций в БД '''
	def select(self, **query):
		''' Выбор транзакций из БД '''
		return (DbTransaction(t) for t in Transaction.query.filter_by(**query).all())

	def incoming(self, wallet_id):
		'''
		Входящие транзакции из БД
		В ней используется src_id в качестве bnf,
		а через интерфейс транзакции эту информацию получить нельзя.
		Этот метод возвращает только проверенные транзакции
		'''
		return (
			IncomingDbTransaction(t)
			for t in Transaction.query.filter_by(
				dst_id=wallet_id,
				dst_status=TransactionDstStatus.GOOD
			).all()
		)

	def unapproved(self, wallet_id):
		''' Неподтвержденные через получателей транзакции '''
		return (
			DbTransaction(t)
			for t in Transaction.query.filter_by(
				dst_id=wallet_id,
				dst_status=TransactionDstStatus.UNKNOWN
			).all()
		)

	def add(self, wallet_id, transaction):
		''' Добавление транзакций в БД '''
		DB.session.add(Transaction(wallet_id, transaction))
		DB.session.commit()


class LimitedNewTransactions:
	'''
	Список новых транзакций, которые проходят по балансу
	Проверенные транзакции, присутствующие в БД исключаются
	Из лимита изначально убирается все, что проверено.
	Новые могу только пройти по остатку, в порядке времени
	'''
	def __init__(self, wallet, limit):
		self.wallet = wallet
		self.limit = limit

	def amounted(self, new, approved):
		''' Транзакции не входящие в approved с суммой '''
		amount = 0
		for tnx in OrderedTransactions(new):
			if next(DbTransactions().select(signature=tnx.signature()), None) is None:
				amount += abs(tnx.amount())
				yield amount, tnx

	def __iter__(self):
		new = OutgoingTransactions(self.wallet.transactions())
		approved = list(DbTransactions().select(src_id=self.wallet.id()))
		newlim = self.limit - sum(-t.amount() for t in approved)
		for amount, tnx in self.amounted(new, approved):
			if amount < newlim and TransactionValid(tnx, self.wallet):
				yield tnx
