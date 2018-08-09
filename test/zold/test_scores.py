# Copyright (c) 2018 Andrey Valyaev <dron.valyaev@gmail.com>
# Copyright (c) 2018 Alexey Tsurkan
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

''' Тестирование Scores'''

from datetime import datetime, timezone
from zold.score import StringScore
from zold.score_props import ScoreValue
from zold.scores import NewerThenScores, WeakScores
from zold.time import DatetimeTime
from .test_score import FakeScore


class TestWeakScores:
	''' Тестирование списка Score, которые нуждаются в прокачке '''
	config = {'STRENGTH': 1}

	def test_empty(self):
		''' Проверка пустого списка '''
		assert not WeakScores([], 16, self.config)

	def test_weak(self):
		''' Проверка слабых score '''
		assert [
			int(ScoreValue(s, self.config))
			for s in WeakScores(
				[
					FakeScore(4, self.config),
					FakeScore(3, self.config),
					FakeScore(2, self.config),
					FakeScore(1, self.config),
					FakeScore(0, self.config)
				],
				3,
				self.config
			)
		] == [2, 1, 0]


class TestNewerThenScores:
	''' Тестирование списка Score, позднее указанной временнОй точки '''
	config = {'STRENGTH': 1}

	def test_newer(self):
		''' проверка фильтра '''
		score = StringScore(
			'2018-08-06T06:45:48Z 37.230.116.39 4096 HdssRDl6@cc53e22229564de6',
			self.config
		)
		assert len(list(NewerThenScores(
			[score],
			DatetimeTime(datetime(2018, 8, 6, 6, 45, 45, tzinfo=timezone.utc))
		))) == 1
		assert not list(NewerThenScores(
			[score],
			DatetimeTime(datetime(2018, 8, 6, 6, 45, 54, tzinfo=timezone.utc))
		))
