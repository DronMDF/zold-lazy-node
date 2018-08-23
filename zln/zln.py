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
from zold.score import JsonScore, MinedScore, XZoldScore
from zold.score_props import ScoreValid, ScoreValue


class NRemotes:
	'''
	Количество активных узлов, определяется методом опроса и
	обновления информации на сервере
	'''
	def __init__(self, argv):
		self.argv = argv

	def __int__(self):
		url = 'http://%s:%s' % tuple(self.argv)
		reply = requests.get(url)
		if reply.status_code != 200:
			raise RuntimeError("Ошибка получения информации")
		score = JsonScore(reply.json()['score'])
		config = {'STRENGTH': score.json()['strength']}

		todo = {'b2.zold.io:4096'}
		done = set()
		while todo:
			host = random.choice(list(todo))
			print(host, "Check...")
			done.add(host)
			todo.remove(host)
			try:
				rremote = requests.get('http://%s/remotes' % host, timeout=5)
			except Exception as err:
				print(host, "Failed:", err)
				continue
			rscore = XZoldScore(rremote.headers['X-Zold-Score'])
			if ScoreValid(rscore, config) and int(ScoreValue(rscore, config)) >= 3:
				print(host, "Good host, update and get remotes...")
				reply = requests.get(
					url,
					headers={'X-Zold-Score': rremote.headers['X-Zold-Score']}
				)
				if reply.status_code != 200:
					print(reply)
				for remote in rremote.json()['all']:
					rhost = '%s:%u' % (remote['host'], remote['port'])
					if rhost not in done:
						if rhost not in todo:
							todo.add(rhost)
							print(host, "New remote: ", rhost)

			else:
				print(host, "Low Score")
		return len(done)


def main(argv):
	''' Основной метод майнера '''
	if argv[0] == 'update':
		return int(NRemotes(argv[1:]))

	# @todo #107: Майнинг необходмо вынести из main
	url = 'http://%s:%s' % tuple(argv)

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
		except Exception as exc:
			print(exc)
			time.sleep(60)


main(sys.argv[1:])
