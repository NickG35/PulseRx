web: daphne -b 0.0.0.0 -p $PORT PulseRx.asgi:application
worker: celery -A PulseRx worker --loglevel=info
