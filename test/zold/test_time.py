# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Score '''
from datetime import datetime, timezone
from zold.time import NowTime, DatetimeTime


class TestNowTime:
	def test_zone(self):
		time = datetime(2018, 6, 19, 14, 17, 22, tzinfo=timezone.utc)
		assert str(DatetimeTime(time)) == '2018-06-19T14:17:22Z'


class TestNowTime:
	def test_zone(self):
		assert str(NowTime()).endswith('Z')
