FROM python:3.15-slim AS kur
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /uvx /bin/

WORKDIR /app

# Önce bağımlılıklar: yalnız pyproject.toml ve uv.lock değişince yeniden kurulur.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

# Sonra proje: kod değişince yalnız buradan sonrası yeniden çalışır.
COPY . .
RUN uv sync --locked --no-dev


# Çalışma aşaması: yalnız kur'un /app'i gelir; uv ve derleme bağlamı gelmez.
# Taban kur ile aynı olmalı: .venv/bin/python taban imajdaki Python'a bir bağlantı.
FROM python:3.15-slim AS calis

# Ev klasörü olmayan bir sistem kullanıcısı. USER'dan önce, root olarak kurulur.
RUN useradd --system --no-create-home uygulama

WORKDIR /app
# Dosyalar root'a ait kalır: uygulama okuyup çalıştırabilir, değiştiremez.
COPY --from=kur /app /app

USER uygulama

ENV PATH="/app/.venv/bin:$PATH"
CMD ["fastapi", "run", "src/yardim_masasi/api.py", "--port", "8000"]
