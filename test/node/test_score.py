# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование корневого урла '''

from node.app import APP
from node.score import AtLeastOneDbScores


class TestNewScore:
	''' Тестирование нового Score '''
	def test_score_content(self):
		''' Новый Score должен содержать значения из конфигурации '''
		with APP.app_context():
			score = next(iter(AtLeastOneDbScores([], {
				'HOST': '7.6.5.4',
				'PORT': 345,
				'WALLET': 'ffffffffffffffff',
				'PUBLIC_KEY': 'public+prefix8b/key==',
				'STRENGTH': 6
			})))
			assert '7.6.5.4 345' in score.prefix()
			assert 'prefix8b@ffffffffffffffff' in score.prefix()
