#!/bin/bash

set -e

export PYTHONPATH=.

pycodestyle node node.test --ignore=W191
pylint node node.test

# @todo #12 Использовать pdd для контроля паззлов
# @todo #9 Использовать radon для контроля цикломатической сложности и уровня
#  поддерживаемости.
# @todo #1 Включить оценку покрытия (coverage, когда появятся тесты)
pytest -v


