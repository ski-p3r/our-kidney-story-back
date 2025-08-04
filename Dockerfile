FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y libpq-dev gcc

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
