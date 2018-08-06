# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Работа с узлами сети '''

from zold.time import StringTime
from zold.score import ScoreValue
from node.db import DB, Remote


class IsRemoteUpdated:
	''' Обновление информации об узле в БД '''
	def __init__(self, score, config):
		self.score = score
		self.config = config

	def __bool__(self):
		jscore = self.score.json()
		remote = Remote.query.filter_by(
			host=jscore['host'],
			port=jscore['port']
		).first()
		if remote is None:
			remote = Remote(jscore['host'], jscore['port'])
			DB.session.add(remote)
		remote.time = StringTime(jscore['time']).as_datetime()
		remote.invoice = jscore['invoice']
		remote.score_value = int(ScoreValue(self.score, self.config))
		DB.session.commit()
		return True
