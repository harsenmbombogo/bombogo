web: gunicorn bombogo.wsgi --log-file - --timeout 120


worker: celery -A bombogo worker --loglevel=info

beat: celery -A bombogo beat --loglevel=info

