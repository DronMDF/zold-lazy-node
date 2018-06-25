# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' WEB интерфейс узла '''

from datetime import datetime
from flask import Flask, jsonify, request
from zold.score import StrongestScore
from node.score import DbScores
from node.db import DB

APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
DB.init_app(APP)
with APP.app_context():
	DB.create_all()


@APP.route('/', methods=['GET'])
def api_root():
	''' Статус ноды '''
	# @todo #3 В этом json необходимо пробросить информацию для майнинга.
	#  Информация для майнинга будет выглядеть как одна строка
	#  (либо голый score, либо hash). Назовем это поле 'mining'
	# @todo #3 version и X-Zold-Version, должны содержать текущую версию zold.
	#  Но хранить ее где-то будет не очень удобно.
	#  Предлагаю использовать версию, которую выдают соседние сервера.
	#  Для этого ее видимо необходимо хранить в БД.
	#  Но пока можно прописать константу.
	data = {
		'version': '0.6.1',
		'score': StrongestScore(DbScores()).json(),
		'farm': {
			# @todo #36 Список current должен содержать базовые хеши
			#  по всем актуальным Score для дальнейшего рассчета.
			#  Пока заглушка.
			'current': [
				datetime.now().isoformat()
			]
		}
	}

	resp = jsonify(data)
	resp.status_code = 200
	resp.headers['X-Zold-Version'] = '0.0.0'

	return resp


@APP.route('/score', methods=['POST'])
def api_score():
	''' Загрузка суффиксов на сервер '''
	try:
		suffix = request.json.get('suffix')
		DbScores().new_suffix(suffix)
		resp = jsonify({})
		resp.status_code = 200
		resp.headers['X-Zold-Version'] = '0.0.0'
		return resp
	except Exception:
		resp = jsonify({})
		resp.status_code = 400
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


@APP.route('/wallet/<w_id>', methods=['GET'])
def api_get_wallet():
	''' Содержимое кошелька '''
	# @todo #6 Необходимо вычитывать содержимое кошелька из БД.
	data = {}

	resp = jsonify(data)
	resp.status_code = 404
	resp.headers['X-Zold-Version'] = '0.0.0'

	return resp


if __name__ == '__main__':
	APP.run(debug=True, host='0.0.0.0', port=5000)
