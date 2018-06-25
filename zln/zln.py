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
import base58
import requests


def sform(suffix_num):
	''' Строковое представление номера, сейчас это 7-значная строка в base58 '''
	return base58.b58encode(suffix_num.to_bytes(8, 'little'))[:7].decode('ascii')


def mine(prefix, start):
	''' Поиск новохо суффикса '''
	return next((
		xs
		for xs in (sform(s) for s in range(start, 0xffffffffffffffff))
		if hashlib.sha256(
			(prefix + ' ' + xs).encode('ascii')
		).hexdigest().endswith('0' * 6)
	))


def main(argv):
	''' Основной метод майнера '''
	url = 'http://%s:%s' % tuple(argv[1:3])

	while True:
		reply = requests.get(url)
		if reply.status_code != 200:
			raise RuntimeError("Ошибка получения информации")

		prefix = random.choice(reply.json().get('farm', {}).get('current', []))
		start_time = datetime.now()
		suffix = mine(prefix, random.randint(0, 0xffffffffffffffff))
		end_time = datetime.now()
		print("Mined: %s take %.2f sec" % (
			suffix,
			(end_time - start_time).total_seconds()
		))
		requests.post(url + '/score', json={'suffix': suffix})


main(sys.argv)
