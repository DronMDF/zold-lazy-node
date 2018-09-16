# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование кошельков (пока здесь только тестовый кошелек) '''

import random
import re
from Crypto.PublicKey import RSA


class FakeWallet:
	''' Случайный кошелек для тестирования '''
	def __init__(self):
		self.id = random.randint(0, 0xffffffffffffffff)
		self.key = RSA.generate(1024)

	def idstr(self):
		''' Идентификатор кошелька '''
		return '%016x' % self.id

	def prefix(self):
		''' Выбираем префикс '''
		key = self.public()
		while True:
			pos = random.randint(0, len(key) - 8)
			prefix = key[pos:pos + 8]
			if re.match('[a-zA-Z0-9]{8,32}', prefix):
				return prefix

	def public(self):
		''' Ключ в формате pem '''
		return self.key.publickey().exportKey('PEM').decode('ascii')

	def __str__(self):
		return '\n'.join(('test', '2', self.idstr(), self.public(), ''))
