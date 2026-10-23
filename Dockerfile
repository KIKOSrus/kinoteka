FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
# миграции при старте, затем gunicorn (воркеры uvicorn)
CMD ["sh", "-c", "alembic upgrade head && gunicorn -c gunicorn.conf.py -b 0.0.0.0:8000 app.main:app"]
