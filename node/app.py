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
