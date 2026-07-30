FROM python:3.12-slim-bookworm

WORKDIR /app

RUN useradd --create-home appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser alembic ./alembic
COPY --chown=appuser:appuser alembic.ini .

USER appuser

EXPOSE 8080

CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
