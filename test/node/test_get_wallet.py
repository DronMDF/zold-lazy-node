# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование Работы с кошельками '''

from flask_api import status
from node.app import APP


class TestGetWallet:
	''' Получение кошелька '''
	WALLET = '\n'.join((
		'zold',
		'2',
		'0000000000000000',
		''.join((
			'MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA96lM5Y+QHYr9WvUucw/wW+dJpnYBa',
			'2/nCij3DXroCaABYL5qG4mVIjGdCBbdS78tcOlcZS+WzPcmyepg56cIwPkpYQop4MawaaCp6Q',
			'C/nybu5sDwvnnDVWCsLveEAPbHos/BpVAJn89NeJO1MaJgaRLKvtRK/P9bgd5tORGJKFq17yi',
			'pfjLtXKSOCX6U2nPUNB8TCaAtESHNdbp6kp2J063k+Mf8CT0yhFrAU5j/nRaUTKTwyyj6dcuR',
			'Tn+FyfFdjfJi2mVOLMJrunNCSr8TNhcMB1fE5MxtwYg46s6ZkqUhQ3oNgSKBgK7DuY2TMVMgs',
			'viIZ1xkUfLR4MCNhjcwi9wVPNkEgTJUdjEK1m4TmNa2DWnX9oCQbYfPhze3Xv4Q3GCAUUSwvx',
			'ZSOqKh/MdqStYOB8ByXp1sEBDsLMpR7DfpmPJm18f5winZ0pEX0U4N/7VTqSIb+w8saT6YqA4',
			'WG+9ZYLKRSxwjYwkbj3cnbeq5bGXd02XjqitTHdonv1EPQvzVMxUO9RUbxjpPHfDIA8AdBX4r',
			'A8F5FYe2K8yMlEgbJy7Za/CAKV9c5Fut5C5eYfxQegu5ffmnQRuTyIZuAjZojIJWctLY2OT9S',
			'qRh0ilqJ4nq4q/eOfUuSJAUEQIZdQX9MBg3lJ0Pw9aSoSAp8iQWRdNTvqvuTZqExs3Tp1UCAw',
			'EAAQ=='
		)),
		''
	))

	def test_wallet_not_found(self):
		''' Кошелек не найден на сервере '''
		response = APP.test_client().get('/wallet/dead3a11ed000000')
		assert response.status_code == status.HTTP_404_NOT_FOUND

	def test_wallet_ok(self):
		''' Сервер возвращает содержимое кошелька '''
		APP.test_client().put('/wallet/0000000000000000', data=self.WALLET)
		response = APP.test_client().get('/wallet/0000000000000000')
		assert response.status_code == status.HTTP_200_OK
		assert response.json['body'] == self.WALLET
