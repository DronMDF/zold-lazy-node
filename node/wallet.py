# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Работа с кошельками '''

from node.db import DB, Wallet, Wanted


class DbWallet:
	''' Представление кошелька '''
	def __init__(self, wallet, config):
		self.wallet = wallet
		self.config = config

	def id(self):
		''' Идентификатор кошелька '''
		return self.wallet.wallet_id

	def public(self):
		''' Публичный ключ '''
		return self.wallet.public

	def __str__(self):
		''' Заголовок кошелька '''
		# @todo #??? Формирование строки должно делаться отдельно от кошелька
		return '\n'.join((
			self.wallet.network,
			self.config['ZOLD_PROTOCOL'],
			self.wallet.wallet_id,
			self.wallet.public,
			''
		))


class DbWallets:
	''' Все кошельки в БД '''
	def __init__(self, config):
		self.config = config

	def __iter__(self):
		return (DbWallet(w, self.config) for w in Wallet.query.all())

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


class DbWanted:
	''' Разыскиваемые кошельки '''
	def __iter__(self):
		return (w.wallet_id for w in Wanted.query.all())

	def add(self, wallet_id):
		''' Добавляет новый кошелек '''
		DB.session.add(Wanted(wallet_id))
		DB.session.commit()
