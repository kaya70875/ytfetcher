FROM python:3.11.9

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock LICENSE README.md /app/
RUN poetry install --no-root --with dev

COPY . /app