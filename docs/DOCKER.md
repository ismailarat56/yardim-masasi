[← README'ye dön](../README.md)

# Kapta Çalıştırma

`compose.yaml` üç servis tanımlar:

| Servis | Ne yapar |
| --- | --- |
| `db` | PostgreSQL 18 (`postgres:18-alpine`). Veriyi `db-data` biriminde tutar, makineye `127.0.0.1:5434`'ten açılır; `pg_isready` ile sağlık denetimi yapılır. |
| `migrate` | Projenin imajıyla `alembic upgrade head` çalıştırır, bekleyen revizyonları uygular ve `0` koduyla çıkar. Veritabanı zaten en son revizyondaysa hiçbir şey uygulamadan çıkar. |
| `api` | Aynı imajla `fastapi run` çalıştırır; `127.0.0.1:8000`'de açılır. Beş saniyede bir kabın içinden `/saglik`'e istek atan bir sağlık kontrolü vardır: komut üç saniyede bitmezse ya da `200` dışında bir yanıt gelirse kontrol başarısız sayılır, üst üste üç başarısızlıkta kap `unhealthy` olur. Compose sağlıksız kabı yeniden başlatmaz, yalnızca işaretler. |

Sık kullanılan komutlar:

| Komut | Etkisi |
| --- | --- |
| `docker compose up -d --build --wait` | İmajı kurar (değişmeyen adımlar önbellekten gelir), üç servisi açar ve `db` ile `api` sağlıklı, `migrate` bitmiş olana kadar bekler. Bir servis sağlıksız kalırsa hata koduyla döner. |
| `docker compose up -d db` | Yalnızca veritabanını açar; API makinede `fastapi dev` ile çalıştırılacaksa bu kullanılır. |
| `docker compose ps -a` | Kapları durumlarıyla listeler; `-a` bitmiş `migrate` kabını da gösterir (`Exited (0)`). |
| `docker compose logs -f api` | API'nin günlüklerini gösterir ve yenilerini izler; `Ctrl+C` ile çıkılır. |
| `docker compose exec api talep-yukle` | Örnek talepleri kabın içinden yükler; komut, `ornek/` klasörü ve `DATABASE_URL` kabın içindedir. |
| `docker compose down` | Kapları ve ağı siler; veriler `db-data` biriminde kalır, sonraki `up` aynı veriyle açılır. |
| `docker compose down -v` | Birimi de siler; bütün veriler gider. Sonraki `up` boş bir veritabanıyla başlar, `migrate` şemayı baştan kurar. |

Servisler sırayla başlar. `migrate`, `depends_on` ile `db`'nin sağlık denetimini (`service_healthy`) bekler; `api` de `migrate`'in başarıyla bitmesini (`service_completed_successfully`). Migration başarısız olursa `api` hiç açılmaz. Yalnızca `depends_on: [db]` yazmak kabın başlamasını beklerdi, PostgreSQL'in bağlantı kabul etmeye hazır olmasını değil.

Kaptaki uygulamalar veritabanına `db:5432`'den bağlanır. Her kabın kendi ağ ortamı vardır: kabın içinde `127.0.0.1` kabın kendisidir, `.env`'deki `127.0.0.1:5434` orada çalışmaz. Compose servisleri ortak bir ağa koyar ve servis adı (`db`) veritabanı kabının adresine çözülür. `5434` yalnızca makinenin kapısıdır; ağın içinden PostgreSQL'in kendi portu `5432` kullanılır. `migrate` ve `api` `.env`'yi `env_file` ile okur, ama `environment` altındaki `DATABASE_URL` `.env`'dekini ezer; `.env`'deki adres makinede çalışan komutlar için kalır.

`Dockerfile` iki aşamalıdır:

- `kur`: `python:3.15-slim` üzerine `ghcr.io/astral-sh/uv:0.13.7`'den `uv` kopyalanır. Önce yalnızca `pyproject.toml` ve `uv.lock` kopyalanıp bağımlılıklar kurulur (`--no-install-project`), kod sonra gelir; böylece kod değiştiğinde bağımlılık katmanı önbellekten gelir, yalnızca proje yeniden kurulur. `--no-dev` geliştirme grubunu (`pytest`, `pyright`) kurmaz, kapta test koşulmaz.
- `calis`: tabanı yine `python:3.15-slim`'dir, çünkü `.venv/bin/python` taban imajdaki Python'a bir bağlantıdır. Bu aşamaya yalnızca `kur`'un `/app` klasörü gelir; `uv` ve derleme bağlamı imaja girmez. Ev klasörü olmayan `uygulama` adında bir sistem kullanıcısı kurulur ve kap onunla çalışır; `/app`'teki dosyalar root'a ait kaldığı için uygulama kodunu okuyup çalıştırabilir, değiştiremez.

`CMD` exec biçimindedir (`["fastapi", "run", ...]`): arada kabuk olmadığı için uygulama kabın 1 numaralı sürecidir ve `docker compose stop`'un gönderdiği `SIGTERM`'i doğrudan alıp düzgünce kapanır. Shell biçiminde (`CMD fastapi run ...`) 1 numaralı süreç `sh` olur, sinyali uygulamaya iletmez; Docker 10 saniye bekleyip `SIGKILL` gönderir ve kap `137` koduyla çıkar.

`.dockerignore`, `.venv`, `.env`, `.env.db`, `.git`, her klasördeki `__pycache__` (`**/__pycache__`) ve `.pytest_cache`'i derleme bağlamının dışında tutar. Böylece parolalar ve API anahtarı imaja girmez, makinedeki sanal ortam kopyalanmaz ve derleyiciye gönderilen bağlam küçülür.

API kapta çalışırken makinenin `8000` portunu `api` kabı tutar; makinede `fastapi dev` açılırsa `address already in use` hatası verir. Makinede geliştirmek için önce kabı durdur:

```bash
docker compose stop api
uv run --env-file .env fastapi dev src/yardim_masasi/api.py
```
