FROM apache/airflow:slim-2.11.0-python3.12

USER root

# Install system dependencies needed for psycopg2, etc.
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt