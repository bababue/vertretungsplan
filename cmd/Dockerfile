FROM ghcr.io/astral-sh/uv:python3.13-alpine
COPY ./ /cmd

WORKDIR /cmd
RUN uv sync --locked

CMD ["uv", "run", "fetchData.py", "0", "5"]