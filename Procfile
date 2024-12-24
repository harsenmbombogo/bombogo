web: gunicorn bombogo.wsgi --log-file -

worker: celery -A bombogo worker --loglevel=info

beat: celery -A bombogo beat --loglevel=info
