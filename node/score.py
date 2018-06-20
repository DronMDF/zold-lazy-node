# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Score '''

import hashlib
from functools import reduce


class JsonScore:
	''' Этот Score конструируется из json '''
	def __init__(self, json):
		self.data = json

	def prefix(self):
		''' Префиксная часть Score '''
		return ' '.join((
			self.data['time'],
			self.data['host'],
			str(self.data['port']),
			self.data['invoice']
		))

	def __str__(self):
		return ' '.join([self.prefix()] + self.data['suffixes'])

	def sha256(self, data):
		''' Рассчет sha256 для строки '''
		hstr = hashlib.sha256(data.encode('ascii')).hexdigest()
		if not hstr.endswith('0' * 6):
			raise RuntimeError('WrongHash')
		return hstr

	def valid(self):
		''' Проверка валидности Score '''
		try:
			reduce(
				lambda p, s: self.sha256(p + ' ' + s),
				[self.prefix()] + self.data['suffixes']
			)
		except Exception:
			return False
		return True
