# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.


''' Работа с датами в формате UTC '''
from datetime import datetime, timedelta, timezone


class DatetimeTime:
	''' Любое произвольное время в формате datetime '''
	def __init__(self, time):
		if time.tzname() is None:
			self.time = time.replace(tzinfo=timezone.utc)
		else:
			self.time = time

	def __str__(self):
		return self.time.isoformat().replace('+00:00', 'Z')

	def as_datetime(self):
		''' Вернуть дату в формате datetime '''
		return self.time


class NowTime:
	''' Текущее время '''
	def __init__(self):
		self.time = DatetimeTime(datetime.now(timezone.utc).replace(microsecond=0))

	def __str__(self):
		return str(self.time)

	def as_datetime(self):
		''' Вернуть дату в формате datetime '''
		return self.time.as_datetime()


class AheadTime:
	''' Момент времени из прошлого (на сколько часов назад) '''
	def __init__(self, hours):
		self.time = DatetimeTime(
			datetime.now(timezone.utc).replace(microsecond=0) - timedelta(hours=hours)
		)

	def __str__(self):
		return str(self.time)

	def as_datetime(self):
		''' Вернуть дату в формате datetime '''
		return self.time.as_datetime()


class StringTime:
	''' Работа с временем в виде строки '''
	def __init__(self, time):
		self.time = time

	def __str__(self):
		return self.time

	def as_datetime(self):
		''' Конвертация строки в datetime (Зона UTC) '''
		return datetime.strptime(
			self.time,
			'%Y-%m-%dT%H:%M:%SZ'
		).replace(tzinfo=timezone.utc)
