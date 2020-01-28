FROM tiangolo/uvicorn-gunicorn-fastapi

COPY poetry.lock pyproject.toml /app/
WORKDIR /app

RUN pip install poetry

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

ENV PYTHONPATH /app
