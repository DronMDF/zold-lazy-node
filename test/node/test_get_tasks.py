# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование Работы со списком задач '''

from flask_api import status
from node.app import APP
from node.db import DB, Score


class TestGetTasks:
	''' Тестирование GET /tasks'''
	def test_mining_tasks(self):
		''' В списке задач присутствуют задачи майнинга '''
		with APP.app_context():
			DB.session.query(Score).delete()
		response = APP.test_client().get('/tasks')
		assert response.status_code == status.HTTP_200_OK
		assert any(t['type'] == 'mining' for t in response.json['tasks'])
