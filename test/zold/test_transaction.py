# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование транзакций '''

from zold.time import NowTime
from zold.transaction import TransactionData


class FakeTransaction:
	''' Транзакция '''
	def __init__(self, src, dst, amount):
		self.tm = NowTime()
		self.zents = amount
		self.src = src
		self.pfx = dst.prefix()
		self.dst = dst

	def id(self):
		''' Идентификатор транзакции '''
		return 1

	def time(self):
		''' Время '''
		return self.tm

	def amount(self):
		''' Баланс '''
		return self.zents

	def prefix(self):
		''' Префикс '''
		return self.pfx

	def bnf(self):
		''' Получатель '''
		return self.dst.id()

	def details(self):
		''' Описание '''
		return 'Test transaction'

	def signature(self):
		''' Сигнатура всегда вычисляется '''
		return self.src.sign(
			str(TransactionData(self.src.id(), self))
		).decode('ascii')


class BadPrefixTransaction(FakeTransaction):
	'''
	Транзакция не совпадающая по префиксу с кошельком назначения
	Наследование используется для того, чтобы корректно считалась сигнатура
	'''
	def prefix(self):
		''' Префикс неправильный '''
		return 'BadPrefix'
