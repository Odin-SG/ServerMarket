FROM python:3.10-slim
WORKDIR /app
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      gcc libpq-dev postgresql-client \
      fonts-liberation bash \
 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/reports
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV SECRET_KEY=p@ss_t-r*ing
ENV REPORTS_FOLDER=/app/reports
ENV DB_HOST=db
ENV DB_PORT=5432
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "run:app"]
