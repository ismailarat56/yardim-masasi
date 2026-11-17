FROM python:3.15-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /uvx /bin/

WORKDIR /app

# Önce bağımlılıklar: yalnız pyproject.toml ve uv.lock değişince yeniden kurulur.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

# Sonra proje: kod değişince yalnız buradan sonrası yeniden çalışır.
COPY . .
RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"
CMD ["fastapi", "run", "src/yardim_masasi/api.py", "--port", "8000"]
