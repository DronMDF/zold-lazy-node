# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование корневого урла '''

from node.score import AtLeastOneDbScores


class TestNewScore:
	''' Тестирование нового Score '''
	def test_score_content(self):
		''' Новый Score должен содержать значения из конфигурации '''
		score = AtLeastOneDbScores([], {
			'HOST': '7.6.5.4',
			'PORT': 345,
			'WALLET': 0xffffffffffffffff,
			'PUBLIC_KEY': 'public key'
		})
		assert '7.6.5.4 345' in score.prefix()
		assert '@ffffffffffffffff' in score.prefix()
		# @todo #51 Протестировать содержимое public_key в score.prefix()
