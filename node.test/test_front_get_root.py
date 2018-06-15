# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование корневого урла '''

from node.app import APP


def test_x_zold_version():
	''' Заголовок должен содержать X-Zold-Version '''
	response = APP.test_client().get('/')
	assert 'X-Zold-Version' in response.headers
