# zold-lazy-node

## Тестовый сервер

```bash
$ gunicorn --pythonpath=. node.app:APP
```

Стоит обратить внимание, что ginicorn должен использовать python3, иначе не взлетит.
