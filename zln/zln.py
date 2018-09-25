#!/usr/bin/env python3
# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Утилита для обслуживания узла '''

from datetime import datetime
import hashlib
import random
import sys
import time
import traceback
import requests
import base58
from zold.score import JsonScore, XZoldScore
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
	def suffix_form(self, suffix_num):
		''' Строковое представление номера, сейчас это 7-значная строка в base58 '''
		return base58.b58encode(suffix_num.to_bytes(8, 'little'))[:7].decode('ascii')

	def new_suffix(self, base, seed, strength):
		''' Вычисление нового суффикса '''
		return next((
			xs
			for xs in (
				self.suffix_form(s)
				for s in range(seed, seed + 1000000)
			)
			if hashlib.sha256(
				(base + ' ' + xs).encode('ascii')
			).hexdigest().endswith('0' * strength)
		), None)

	def run(self, args):
		''' Основная процедура сценария '''
		url = 'http://%s:%s' % tuple(args)

		while True:
			try:
				info = requests.get(url)
				if info.status_code != 200:
					raise RuntimeError("Ошибка получения информации")
				score = JsonScore(info.json()['score'])

				reply = requests.get(url + '/tasks')
				if reply.status_code != 200:
					raise RuntimeError("Ошибка получения информации")
				tasks = [t for t in reply.json()['tasks'] if t['type'] == 'mining']
				if tasks:
					task_base = random.choice(tasks)['base']
					start_time = datetime.now()
					suffix = self.new_suffix(
						task_base,
						random.randint(0, 0xffffffffffffffff),
						score.json()['strength']
					)
					end_time = datetime.now()
					if suffix is not None:
						print("%s: Mined: %s take %.2f sec" % (
							end_time.isoformat(' '),
							suffix,
							(end_time - start_time).total_seconds()
						))
						requests.post(url + '/score', json={'suffix': suffix})
					else:
						print("%s: Mined: none in %.2f sec" % (
							end_time.isoformat(' '),
							(end_time - start_time).total_seconds(),
						))
					continue
			except Exception as exc:
				traceback.print_exc(exc)
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
