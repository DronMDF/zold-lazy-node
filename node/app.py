# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' WEB интерфейс узла '''

from flask import Flask, jsonify

APP = Flask(__name__)


@APP.route('/', methods=['GET'])
def api_root():
	''' Статус ноды '''
	# @todo #3 Необходимо вычитывать информацию о score из БД.
	#  И видимо тут необходимо сделать несколько таблиц.
	#  Первая таблица содержит score, который состоит из:
	#  time, host, port, invoice
	#  Вторая таблица содержит суффиксы:
	#  @score, order, suffix
	#  одновременно в работе может быть несколько score, мы показываем тот,
	#  который создан раньше всех и время создания которого не превышает суток.
	#  те. выбираем самый старый в пределах суток, и все суффиксы к нему
	#  и пихаем сюда.
	# @todo #3 В этом json необходимо пробросить информацию для майнинга.
	#  Информация для майнинга будет выглядеть как одна строка
	#  (либо голый score, либо hash). Назовем это поле 'mining'
	# @todo #3 version и X-Zold-Version, должны содержать текущую версию zold.
	#  Но хранить ее где-то будет не очень удобно.
	#  Предлагаю использовать версию, которую выдают соседние сервера.
	#  Для этого ее видимо необходимо хранить в БД.
	#  Но пока можно прописать константу.
	data = {
		"version": "0.6.1",
		"score": {
			"value": 3,
			"time": "2017-07-19T21:24:51Z",
			"host": "b2.zold.io",
			"port": 4096,
			"invoice": "THdonv1E@0000000000000000",
			"suffixes": ["4f9c38", "49c074", "24829a"],
			"strength": 6
		}
	}

	resp = jsonify(data)
	resp.status_code = 200
	resp.headers['X-Zold-Version'] = '0.0.0'

	return resp


@APP.route('/remotes', methods=['GET'])
def api_remotes():
	''' Список известных и проверенных нод '''
	data = {
		"version": "0.13.5",
		"all": [
			{"host": "b2.zold.io", "port": 4096, "score": 0},
			{"host": "b1.zold.io", "port": 80, "score": 0}
		]
	}
	# @todo #4 Это копипаста... я вижу эти три строки уже два раза.
	#  И подозреваю, что будет больше. Необходимо вынести этот функционал
	#  в отдельный класс.  К тому же заголовок тоже будет больше...
	#  Есть запрос 228 на заголовок X-Zold-Network.
	#  zold потенциально поддерживает разные сети.
	resp = jsonify(data)
	resp.status_code = 200
	resp.headers['X-Zold-Version'] = '0.0.0'

	return resp


if __name__ == '__main__':
	APP.run(debug=True, host='0.0.0.0', port=5000)
