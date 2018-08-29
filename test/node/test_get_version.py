# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование Работы с версией '''

import re
from flask_api import status
from node.app import APP


class TestGetVersion:
	''' Тестирование GET /version '''
	def test_version_format_is_text(self):
		''' При запросе сервер возвращает свою  версию в виде текста '''
		response = APP.test_client().get('/version')
		assert response.status_code == status.HTTP_200_OK
		assert re.match(r'^\d+\.\d+\.\d+$', response.data.decode('ascii'))
