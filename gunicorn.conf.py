# Запуск: gunicorn -c gunicorn.conf.py app.main:app
bind = "127.0.0.1:8000"
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"  # FastAPI — ASGI, поэтому воркер uvicorn
accesslog = "-"
errorlog = "-"
