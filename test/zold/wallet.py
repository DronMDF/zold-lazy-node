# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестовые кошельки '''

import base64
import random
import re
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


class TestWallet:
	''' Случайный кошелек для тестирования '''
	def __init__(self, wallet_id, key):
		self.wallet_id = wallet_id
		self.key = key

	def id(self):
		''' Идентификатор кошелька '''
		return '%016x' % self.wallet_id

	def public(self):
		''' Ключ в формате pem, без заголовков одной строкой '''
		return base64.b64encode(
			self.key.publickey().exportKey('DER')
		).decode('ascii')

	def transactions(self):
		''' Список транзакций '''
		return []

	def prefix(self):
		''' Выбираем префикс '''
		key = self.public()
		while True:
			pos = random.randint(0, len(key) - 8)
			prefix = key[pos:pos + 8]
			if re.match('[a-zA-Z0-9]{8,32}', prefix):
				return prefix

	def sign(self, data):
		''' Подпись для блока данных '''
		return base64.b64encode(
			PKCS1_v1_5.new(self.key).sign(SHA256.new(data.encode('ascii')))
		)

	def __str__(self):
		return '\n'.join(('test', '2', self.id(), self.public(), ''))


class FakeWallet:
	''' Случайный кошелек для тестирования '''
	def __init__(self):
		self.wallet = TestWallet(
			random.randint(0, 0xffffffffffffffff),
			RSA.generate(1024)
		)

	def __getattr__(self, name):
		return getattr(self.wallet, name)

	def __str__(self):
		return str(self.wallet)


class RootWallet:
	''' Корневой кошелек '''
	def __init__(self):
		# Для того, чтобы повторные запуски теста проходили
		# Мы заложим тестовый ключ в код,
		# но транзакции для воспроизводимости надо сносить
		self.wallet = TestWallet(
			0x0000000000000000,
			RSA.importKey('\n'.join((
				'-----BEGIN RSA PRIVATE KEY-----',
				'MIICXQIBAAKBgQDCERVEEjG06u8nNwhimYYkOBI8bWJb2uYCU2UgsoSzzkGBL4FF',
				'F9C3rXtXUvTuDAjZ4vloM0NtbLxnJffpxYwzzN0ellvbwkVxWT9PMdq+k5VeCXxn',
				'UWSErUf/aPWLq2rkyzVfcdmVgmrGsEFYWDG5EHDi3EJHYH1AGjqVi4g6CQIDAQAB',
				'AoGAIx6cTplMTYVGij43UkCeOee7xRu2dREEFt+oqWYlBbUJvasvJaXNq6/FZmQo',
				'1vtujp+4qta8GQ1YewIv/yo02MoRrW419bAbmgiH82WFo7KMm0lQ7RSjADqdym+5',
				'oIeLKWWbBnpnHoN7KuHFcg3kd8UGtbS1Pzxw6hMscynRPpECQQDPDtq2rVkhSVFW',
				'/xvuTIQWDswdQVWzI0JnfGA+PI5rhpLTmBRWurDevtQMsJ/w+Q0UFaKxVK4ckMae',
				'ChnIsYd3AkEA7/AfGFWU43B3S9tFBK1fAiNpTRmwiZ4kiVtFFLRSRRQ4DGnVIkCh',
				'7aEarkO1TyoLXCQbOflXnCkeIoNoBseqfwJBALB6Zqvgn+EhDnTpxrKbANGUFyCw',
				'OQ0P9l8hwR4KmxDGiIpUSrGJOYsAdtfCCvBmNWFy91HRbPzn4IF+9m758Q0CQQDA',
				'3fugy+pKiHTcfP0VrWbZiS1z1FqbxIsJ/luhMPGQpZgIImo4hkujgAS6X6K2Z82J',
				'21wnVc6esE6Q36AXExhxAkBQgxp3RDHXjEjglm4qggeB5fgXtQATOrZ9tfdIXy26',
				'TiOIBNEn3aqhiuE0H0/ElpG82oWJ3abevrwVettFdW0y',
				'-----END RSA PRIVATE KEY-----'
			)))
		)

	def __getattr__(self, name):
		return getattr(self.wallet, name)

	def __str__(self):
		return str(self.wallet)
