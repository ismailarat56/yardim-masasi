[← README'ye dön](../README.md)

# Kurulum ve Ortam

## Gerekenler

- [uv](https://docs.astral.sh/uv/): Python ve proje bağımlılıklarını yönetir.
- Python 3.15: geliştirme sürümü `.python-version` dosyasında seçilidir. `pyproject.toml` en az Python 3.15 ister. Uygun yorumlayıcı yoksa uv, otomatik indirme açıkken onu kurabilir.
- İlk kurulumda paketleri indirmek ve kullanım sırasında PyPI'ya erişmek için internet bağlantısı.
- [Docker](https://docs.docker.com/get-docker/) ve Docker Compose: API'nin kullandığı PostgreSQL veritabanını bir kapta çalıştırır; istenirse API de bir kapta çalışır.

## Kurulum

```bash
git clone https://github.com/ismailarat56/yardim-masasi.git
cd yardim-masasi
uv sync --locked
```

`uv sync --locked`, `uv.lock` dosyasındaki sürümlerle `.venv` sanal ortamını hazırlar; geliştirme bağımlılıkları `pytest` ve `pyright` da kurulur. Kilit dosyası proje tanımıyla uyuşmuyorsa hata verir ve kilidi değiştirmez.

`.venv` Git'e dahil edilmez. Başka bir bilgisayarda aynı komutla yeniden oluşturulur. Komutları `uv run` ile çalıştırırken sanal ortamı elle etkinleştirmek gerekmez.

## Çalıştırma

    uv run yardim-masasi httpx fastapi
    uv run yardim-masasi -e 2 httpx fastapi rich
    uv run talep-ozeti
    uv run talep-ozeti ornek/talepler.json
    uv run talep-ozeti ornek/talepler.jsonl
    uv run talep-ozeti --durum kapali
    uv run talep-ozeti --oncelik yuksek --etiket hesap
    uv run talep-ozeti ornek/talepler-zamanli.jsonl --son-gun 10
    uv run talep-ozeti --version
    uv run python -m yardim_masasi --help

`talep-ozeti`'ne dosya verilmezse `ornek/talepler.json` okunur.

`uv run python -m yardim_masasi httpx`, `yardim-masasi` ile aynı PyPI
sorgulama girişini çalıştırır. Talep özeti için `uv run talep-ozeti` kullanılır.

## Ortam Değişkenleri

İsteğe bağlı yerel ayarlar için, `.env` henüz yoksa örnek dosyayı kopyala:

```bash
cp .env.example .env
```

| Değişken | Varsayılan | Açıklama |
| --- | --- | --- |
| `PYPI_ZAMAN_ASIMI` | `10` | HTTP isteğinin zaman aşımı ayarı, saniye cinsinden. `2.5` gibi ondalık değerler kullanılabilir. |
| `DATABASE_URL` | yok | API'nin, `talep-yukle`'nin ve `alembic` komutlarının bağlandığı veritabanı, ör. `postgresql://yardim:yardim@127.0.0.1:5434/yardim_masasi`. Tanımlı değilse üçü de çalışmaz. |
| `TEST_DATABASE_URL` | yok | PostgreSQL testlerinin veritabanı, ör. `.../yardim_masasi_test`. Bu veritabanının `public` şeması her test oturumunda silinip migration'larla yeniden kurulur; adres **asla asıl veritabanını göstermemelidir**, yoksa bütün veriler silinir. Tanımlı değilse bu testler atlanır. |
| `API_ANAHTARI` | yok | `POST` ve `PATCH` için beklenen `X-API-Anahtari` değeri. Tanımlı değilse yazma uçları her isteğe `401` döner. |

Kabın kendi ayarları ayrı bir dosyadadır: `.env.db`, `POSTGRES_USER`, `POSTGRES_PASSWORD` ve `POSTGRES_DB` değerlerini taşır ve `.env.db.example`'dan kopyalanır. PostgreSQL bu değerleri yalnızca veri birimi boşken, ilk açılışta kullanır; sonradan değiştirmek var olan kullanıcının parolasını değiştirmez. Bağlantı adreslerindeki kullanıcı adı ve parola bu dosyadakilerle aynı olmalıdır.

uv `.env` dosyasını kendiliğinden okumaz; dosyayı açıkça belirt:

```bash
uv run --locked --env-file .env yardim-masasi httpx
```

Dosya oluşturmadan tek komuta değer vermek de mümkündür (Bash):

```bash
PYPI_ZAMAN_ASIMI=2.5 uv run --locked yardim-masasi httpx
```

`.env` ve `.env.db` Git'e dahil edilmez; paylaşılabilir ayar örnekleri `.env.example` ve `.env.db.example` içinde tutulur.
