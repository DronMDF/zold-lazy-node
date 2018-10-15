# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Работа с кошельками '''

from node.db import DB, Wallet, Wanted
from zold.transaction import StringTransaction, TransactionString


class DbWallet:
	''' Представление кошелька '''
	def __init__(self, wallet, config):
		self.wallet = wallet
		self.config = config

	def network(self):
		''' Название сети '''
		return self.wallet.network

	def id(self):
		''' Идентификатор кошелька '''
		return self.wallet.wallet_id

	def public(self):
		''' Публичный ключ '''
		return self.wallet.public

	def transactions(self):
		''' Список транзакций '''
		# @todo #218: Прочитать список транзакций из БД
		return []


class DbWallets:
	''' Все кошельки в БД '''
	def __init__(self, config):
		self.config = config

	def __iter__(self):
		return (DbWallet(w, self.config) for w in Wallet.query.all())

	def count(self):
		''' Общее количество кошельков '''
		# Такой подсчет количества может оказаться медленным
		return Wallet.query.count()

	def wallet(self, id):
		''' Возвращает конкретный кошелек '''
		# @todo #146 Использовать one при конкретном запросе кошелька
		#  Сейчас это не срабатывает, потому что не контролируется содержимое БД
		#  Кошельки в БД дублируются
		wallet = Wallet.query.filter_by(wallet_id=id).first()
		if wallet is None:
			raise RuntimeError("Walet not found")
		return DbWallet(wallet, self.config)

	def add(self, wallet):
		''' Добавляет новый кошелек '''
		DB.session.add(Wallet(wallet.id(), wallet.network(), wallet.public()))
		DB.session.commit()


class DbWantedWallet:
	''' Отдельная запись из таблицы поиска '''
	def __init__(self, wanted):
		self.wanted = wanted

	def id(self):
		''' Идентификатор разыскиваемого кошелька '''
		return self.wanted.wallet_id

	def transaction(self):
		''' Транзакция, по которой разыскивается кошелек '''
		return StringTransaction(self.wanted.transaction)

	def who(self):
		''' Кто запросил поиск транзакции '''
		return self.wanted.who

	def remove(self):
		''' Удаление текущей записи'''
		DB.session.delete(self.wanted)
		DB.session.commit()


class DbWanted:
	''' Разыскиваемые кошельки '''
	def __iter__(self):
		try:
			return (DbWantedWallet(w) for w in Wanted.query.all())
		except Exception:
			return self

	def __next__(self):
		raise StopIteration

	def add(self, wallet_id, transaction, who):
		''' Добавляет новый кошелек '''
		DB.session.add(Wanted(wallet_id, str(TransactionString(transaction)), who))
		DB.session.commit()
