FROM python:3.11-slim

# Needed for psycopg2
RUN apt-get clean && apt-get update --fix-missing && apt-get install -y libpq-dev gcc build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
CMD python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    gunicorn config.wsgi:application --bind 0.0.0.0:8000
