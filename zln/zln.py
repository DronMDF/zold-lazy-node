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
from zold.score import JsonScore, StringScore, MinedScore
from zold.score_props import ScoreValid, ScoreValue


def update_remotes(url):
	reply = requests.get(url)
	if reply.status_code != 200:
		raise RuntimeError("Ошибка получения информации")
	score = JsonScore(reply.json()['score'])
	config = {'STRENGTH': score.json()['strength']}

	todo = {'b2.zold.io:4096'}
	done = set()
	while todo:
		host = random.choice(list(todo))
		print("Select %s for update" % host)
		done.add(host)
		todo.remove(host)
		rremote = requests.get('http://%s/remotes' % host)
		rscore = StringScore(rremote.headers['X-Zold-Score'], config)
		print("Remote score: %s" % str(rscore))
		print(bool(ScoreValid(rscore, config)))
		print(int(ScoreValue(rscore, config)))
		if ScoreValid(rscore, config) and int(ScoreValue(rscore, config)) >= 3:
			print("Update remotes from %s" % host);
			for r in rremote.json()['all']:
				rhost = '%s:%u' % (r['host'], r['port'])
				if rhost not in done:
					todo.add(rhost)
		else:
			print("Low Score")


class NRemotes:
	'''
	Количество активных узлов, определяется методом опроса и
	обновления информации на сервере
	'''
	def __init__(self, argv):
		self.argv = argv

	def __int__(self):
		pass


def main(argv):
	''' Основной метод майнера '''
	if argv[0] == 'propogate':
		return int(NRemotes(argv[1:]))

	# @todo #107: Майнинг необходмо вынести из main
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
				# @todo #107 Режимы zln в командной строке
				#  Необходимо ввести аргументы командной строки, чтобы
				#  выбирать объем функционала, который мы хотим активировать.
				update_remotes(url)
				time.sleep(60)
		except Exception as exc:
			print(exc)
			time.sleep(60)


main(sys.argv[1:])
