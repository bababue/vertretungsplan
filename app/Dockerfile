FROM ghcr.io/astral-sh/uv:python3.13-alpine
COPY ./ /app

WORKDIR /app
RUN uv sync --locked

CMD ["uv", "run", "gunicorn", "-b", "0.0.0.0:8000", "app:app"]

EXPOSE 80:8000
