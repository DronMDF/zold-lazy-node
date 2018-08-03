#!/usr/bin/env python3
# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Утилита для обслуживания узла '''

from datetime import datetime
import random
import sys
import time
import requests
from zold.score import JsonScore, MinedScore


def main(argv):
	''' Основной метод майнера '''
	url = 'http://%s:%s' % tuple(argv[1:3])

	while True:
		try:
			reply = requests.get(url)
			if reply.status_code != 200:
				raise RuntimeError("Ошибка получения информации")

			json_scores = reply.json().get('farm', {}).get('current', [])
			if json_scores:
				json_score = random.choice(json_scores)
				start_time = datetime.now()
				suffix = MinedScore(
					JsonScore(json_score),
					{'STRENGTH': json_score['strength']}
				).suffixes()[-1]
				end_time = datetime.now()
				print("Mined: %s take %.2f sec" % (
					suffix,
					(end_time - start_time).total_seconds()
				))
				requests.post(url + '/score', json={'suffix': suffix})
			else:
				time.sleep(60)
		except Exception as e:
			print(e)


main(sys.argv)
