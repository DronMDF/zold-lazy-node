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
		'0.11.13',
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
		'',
		''.join((
			'0001;2018-05-27T15:11:36Z;fffffc0000000000;XC1Vk4CU;00000000000ff1ce;',
			'emission 1;5SsewlCnY+9rnY7JvFqBjT1fOCUUF4ZX2ZF89EsfYuFweRvraFh9YZBgOodd2C',
			'NCo9zQ0NZdhLpuRUzbulEm+tofPV3KzyxbNwstiuB5FWD7F5JJLj6YvxNVRPbVDM/bN22MThi',
			'EBpiVZlPuiHKv0Od57O+z7VEYJwTKtsw2gQ28nA0U47nJ/x0u0qQVFCu/k1kB9x7pQAhFtRVL',
			'DhSkhvEkgF08G/np10mrz9J1sL5JFXMokKDeZS0oxehPOH1h0eIpvTCAH9eTV0fCP6conzpFN',
			'RNFNk6W+6txq1HuLJpnh9me60KOI6MlC+JPE/koQNAAi7xYk9oqpXVS+oubjbaydYeDu6BmwZ',
			'NqwX5GkEwnSQgY/MGI4v43nTZvp/RA1zfYfutI61WFMQ/eaXcTxSxmF5zrpi0Sd9vpxBUVHOS',
			'd3h/VwmpDDD0+qLhFR6q6ewszdAyK9OitfHIFMxk9b3kvgD/tZ96G3T/JNZ7zHG5/qP8nY0O/',
			'iwppgRWJbxDNj1VetkZlVN3vUdJuaSvXE9/b870Bf4dbmPk1M4dKvJGIWg47hiNHQxDhCKjLF',
			'ZTy47RjxUanK/HjpchXPK2kL+wXxn8pJqCYgJiN2GYx2lJ1crKVbWhYU4MCEBnoGEHSXuFPMW',
			'03Ze5cWF9lbjMmOZcoIFjcJ5JRoKL80RGLeyI='
		))
	))

	def test_wallet_not_found(self):
		''' Кошелек не найден на сервере '''
		response = APP.test_client().get('/wallet/dead3a11ed000000')
		assert response.status_code == status.HTTP_404_NOT_FOUND

	def test_wallet_ok(self):
		''' Сервер возвращает содержимое кошелька '''
		APP.test_client().post('/wallet/0000000000000000', data=self.WALLET)
		response = APP.test_client().get('/wallet/0000000000000000')
		assert response.status_code == status.HTTP_200_OK
		assert response.json.body == self.WALLET
