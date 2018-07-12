# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование Работы с кошельками '''

from node.app import APP
from zold.score import JsonScore, ScoreValid


class TestPutWallet:
	''' Тестируем PUT /wallet/<id> '''
	EMPTY_WALLET = '\n'.join((
		'zold',
		'1',
		'cb91e8b5b4b66866'
		''.join((
			'MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA2Z999vmvkavYi4Uh7uV2mPPKYMAKS',
			'rnbO2Iwi97PlXOACocXYCaRaoWHCrbtHuKR3dtjrU9hVygvl0UlmeMnvilOLobMMIBrr+TTjp',
			'bztHSKjXdhT7cxxWLMG5hqcaO9E6HxCpKXn/DbCK0il6nhcZGz/zciCa/vpo1WB05TWpIMcaR',
			'ouI/uKLlQsglegD9OB3aiXuYWnYvJBOZIzuCf3/M/KljH6/MfopR6LlxbZgAWLEbLxn7r9OHE',
			'eD+/2PX3DgD4OOtvvM9HSnvcoXNgL2MHyo6TzKmNE+BamwO5WfB8Wb71CED9k/qa9YOSMKPJH',
			'MGkIEoFqF7G7hA+vsCbLp1MWtv0100GM/Vgxy5Ae/7g6EmYEUOgx7mIzWyKorHayWq5TBchFm',
			'qGB6aTkMbhKKyfIl1djBe3TXAqXVq1nncuz25ZxybFwKA6Z52OB4S3tAWE5qRsnBe6ppoiY9/',
			'FuwQRS9stIBoY3hEfo58BVxjnLTbymvV8bvgLYXLgtcjjyLhzmUyzXhJpzXgORVLsQLp7NA2q',
			'gtUBQJdpyZHbbddiwHUnwQn8/Q+of5SpwJXdJOwtY25ME6e6DW/5SxZPnhU9GhR92M/RL0dGf',
			'hRqgWSpu85CE0peNDgjcR4qzIGKlKVrGdcVn9yqLQznuNUb0y6PCtVMn9eL6PXmB35WMzUCAw',
			'EAAQ=='
		))
	))

	def test_server_return_score(self):
		''' Сервер возвращает содержимое кошелька '''
		response = APP.test_client().put(
			'/wallet/cb91e8b5b4b66866',
			data=self.EMPTY_WALLET
		)
		assert ScoreValid(JsonScore(response.json['score']))
