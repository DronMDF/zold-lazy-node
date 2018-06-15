import pytest
from node.app import APP


def test_x_zold_version():
	''' Заголовок должен содержать X-Zold-Version '''
	response = APP.test_client().get('/')
	assert 'X-Zold-Version' in response.headers
