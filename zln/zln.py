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
from zold.time import StringTime


class XZoldRequestScore:
	'''
	Почему-то на выход Score нужно посылать в другом формате
	Это странно и не логично, но так.
	Я написал багу, но не хочу ждать когда ее исправят.
	Поэтому эмулируем этот кривой формат
	'''
	def __init__(self, score):
		self.score = score

	def __str__(self):
		jscore = self.score.json()
		return ' '.join(
			[
				str(jscore['strength']),
				'%x' % int(StringTime(jscore['time']).as_datetime().timestamp()),
				jscore['host'],
				'%x' % jscore['port']
			] + list(jscore['invoice'].split('@')) + jscore['suffixes']
		)


class NRemotes:
	'''
	Количество активных узлов, определяется методом опроса и
	обновления информации на сервере
	'''
	def __init__(self, argv):
		self.argv = argv

	def __int__(self):
		# @todo #107 Функция слишком длинная, необходима реорганизация
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
				rremote = requests.get(
					'http://%s/remotes' % host,
					timeout=30,
					headers={
						# @todo #88 Формат score отправку отличается от реплайного
						#  Необходимо убрать, когда исправят багу в zold
						'X-Zold-Score': str(XZoldRequestScore(score))
					}
				)
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


class ScenarioUpdate:
	''' Сценарий обновления списка нод '''
	def run(self, args):
		''' Основная процедура сценария '''
		return int(NRemotes(args))


class ScenarioMining:
	''' Сценарий майнинга '''
	def run(self, args):
		''' Основная процедура сценария '''
		url = 'http://%s:%s' % tuple(args)

		while True:
			try:
				# @todo #122 Информацию для майнинга необходимо запрашивать через /tasks
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
			except Exception as exc:
				print(exc)
			time.sleep(60)


class Scenarios:
	''' Метасценарий, разрыливает на нижележащие '''
	def __init__(self, **scenarios):
		self.scenarios = scenarios

	def run(self, args):
		''' Главный метод метасценария '''
		if args[0] in self.scenarios:
			self.scenarios[args[0]].run(args[1:])


Scenarios(
	update=ScenarioUpdate(),
	mine=ScenarioMining()
).run(sys.argv[1:])
