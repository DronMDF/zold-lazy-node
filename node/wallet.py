# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Работа с кошельками '''

from sqlalchemy.orm.exc import NoResultFound
from node.db import DB, Wallet


class DbWallet:
	''' Представление кошелька '''
	def __init__(self, wallet):
		self.wallet = wallet

	def id(self):
		''' Идентификатор кошелька '''
		return self.wallet.wallet_id

	def body(self):
		''' Заголовок кошелька '''
		return '\n'.join((
			self.wallet.network,
			'2',
			self.wallet.wallet_id,
			self.wallet.public,
			''
		))


class DbWallets:
	''' Все кошельки в БД '''
	def __iter__(self):
		return (DbWallet(w) for w in Wallet.query.all())

	def wallet(self, id):
		''' Возвращает конкретный кошелек '''
		try:
			return DbWallet(Wallet.query.filter_by(wallet_id=id).one())
		except NoResultFound as err:
			raise RuntimeError("Walet not found") from err

	def add(self, wallet):
		''' Добавляет новый кошелек '''
		DB.session.add(Wallet(wallet.id(), wallet.network(), wallet.public()))
		DB.session.commit()
