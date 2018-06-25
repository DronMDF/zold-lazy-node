# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.


''' Score из БД'''
from zold.score import JsonScore
from node.db import DB, Suffix


class DbScores:
	''' Список всех Score из БД '''
	def __iter__(self):
		# @todo #29 Вычитать из БД все имеющиеся score
		#  А пока это заглушка, которую необходимо потом убрать
		yield JsonScore({
			"host": "178.128.169.239",
			"port": 4096,
			"invoice": "Rg3XJle8@48b368ce23ed97fe",
			"time": "2018-06-20T20:01:32Z",
			"suffixes": []
		})

	def new_suffix(self, suffix):
		''' Добавляем новый суффикс в БД '''
		DB.session.add(Suffix(suffix))
		DB.session.commit()
