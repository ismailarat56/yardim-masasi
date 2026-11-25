<div align="center">

# Yardım Masası

**PyPI sürüm sorgusu, destek talebi özeti ve talepleri PostgreSQL'de saklayan bir FastAPI uygulaması. Tek Python paketinde.**

![Python](https://img.shields.io/badge/Python-3.15-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Lisans](https://img.shields.io/badge/lisans-MIT-2ea44f)

[Öne çıkanlar](#öne-çıkanlar) · [Kurulum ve çalıştırma](#kurulum-ve-çalıştırma) · [Komutlar](#komutlar) · [API özeti](#api-özeti) · [Testler](#testler)

</div>

Yardım Masası üç parçadan oluşur. `yardim-masasi` komutu verilen Python paketlerinin PyPI'daki güncel sürümünü ve desteklediği Python sürüm aralığını gösterir. `talep-ozeti` komutu bir JSON ya da JSON Lines dosyasındaki destek taleplerini özetler. FastAPI uygulaması talepleri PostgreSQL'de saklar ve HTTP üzerinden sunar.

Proje aynı zamanda Python yorumlayıcısı, sanal ortam, `uv`, bağımlılık yönetimi ve ortam değişkenleri üzerine bir çalışma örneğidir. Python 3.15, FastAPI, psycopg, Alembic, httpx ve uv ile yazıldı.

## Öne çıkanlar

- **PyPI sorgusu:** paketleri kurmadan sorgular; istekler eşzamanlı yürür (varsayılan sınır 4), çıktı komuttaki paket sırasıyla yazılır.
- **Yeniden deneme:** bağlantı ve zaman aşımı hataları yarım saniye arayla iki kez daha denenir; HTTP durum hataları yeniden denenmez.
- **Talep özeti:** talepleri durumlarına göre sayar, kapanmamışları öncelik sırasıyla listeler; durum, öncelik, etiket ve son N gün filtreleri birlikte uygulanır.
- **Doğrulama ve çıkış kodları:** her talep okunurken doğrulanır; komutlar başarıda `0`, veri ya da ağ hatasında `1`, kullanım hatasında `2` döndürür.
- **HTTP API:** sekiz uç; talep listeleme, okuma, oluşturma, güncelleme, durum özeti, yorumlar ve sağlık denetimi.
- **Sayfalama:** ayraç bir sayfa numarası değil, son talebin `(acildi, id)` çiftidir; iki sayfa arasında yeni talep açılsa da sayfalar kaymaz.
- **Arama:** talep başlıklarında PostgreSQL'in Türkçe tam metin aramasıyla; `or`, `-kelime` ve tırnaklı ifade yazımları çalışır.
- **Koşullu istekler:** `ETag`, `If-Match` ve `If-None-Match`; eski sürümle gelen `PATCH` `412` alır, hiçbir şey yazılmaz.
- **Migration'lar:** şema beş Alembic revizyonuyla kurulur; testler her revizyonun geri alınıp yeniden uygulanabildiğini denetler.
- **Kaplar:** `docker compose up` veritabanını, migration'ları ve API'yi sırayla açar; imaj iki aşamalıdır ve root olmayan bir kullanıcıyla çalışır.
- **Testler ve tip denetimi:** pytest ve pyright; depo testleri aynı sözleşmeyi hem bellekte hem PostgreSQL'de koşturur.

## Gereksinimler

- [uv](https://docs.astral.sh/uv/): Python ve proje bağımlılıklarını yönetir.
- Python 3.15: `.python-version` dosyasında seçilidir. Uygun yorumlayıcı yoksa uv, otomatik indirme açıkken onu kurabilir.
- [Docker](https://docs.docker.com/get-docker/) ve Docker Compose: PostgreSQL veritabanı ve istenirse API kapta çalışır.
- İlk kurulumda paketleri indirmek ve PyPI sorguları için internet bağlantısı.

## Kurulum ve çalıştırma

```bash
git clone https://github.com/ismailarat56/yardim-masasi.git
cd yardim-masasi
uv sync --locked
```

Komut satırı araçları veritabanı gerektirmez:

```bash
uv run yardim-masasi httpx fastapi
uv run talep-ozeti
uv run talep-ozeti --oncelik yuksek --etiket hesap
uv run talep-ozeti ornek/talepler-zamanli.jsonl --son-gun 10
```

API'yi veritabanı ve migration'larla birlikte kaplarda açmak için:

```bash
cp .env.example .env
cp .env.db.example .env.db
docker compose up -d --build --wait
docker compose exec api talep-yukle
```

Sunucu `http://127.0.0.1:8000` adresinde açılır; `http://127.0.0.1:8000/docs` uçları tarayıcıdan denemeye yarayan otomatik belgeyi gösterir. `talep-yukle` örnek talepleri yükler.

API'yi makinede, kod değiştikçe yeniden başlayacak biçimde çalıştırmak için aynı `.env` ve `.env.db` dosyalarıyla yalnızca veritabanı kapta açılır. API kabı açıksa önce `docker compose stop api` ile durdurulur.

```bash
docker compose up -d db
uv run --env-file .env alembic upgrade head
uv run --env-file .env fastapi dev src/yardim_masasi/api.py
```

Ayrıntılar: [docs/KURULUM.md](docs/KURULUM.md) (kurulum ve ortam değişkenleri), [docs/VERITABANI.md](docs/VERITABANI.md) (veritabanı ve migration'lar), [docs/DOCKER.md](docs/DOCKER.md) (servisler ve imaj).

## Komutlar

| Komut | İşlev |
|---|---|
| `yardim-masasi [-e N] PAKET [PAKET ...]` | Paketlerin PyPI'daki güncel sürümünü ve Python sürüm aralığını gösterir. `-e` eşzamanlı sorgu sınırıdır. |
| `talep-ozeti [dosya]` | `.json` ya da `.jsonl` dosyasındaki talepleri özetler. Dosya verilmezse `ornek/talepler.json` okunur. |
| `talep-yukle [dosya]` | Örnek talepleri veritabanına yükler. Dosya verilmezse `ornek/talepler-zamanli.jsonl` okunur. |

`talep-ozeti` bayrakları: `--durum`, `--oncelik`, `--etiket`, `--son-gun N`, `-v` / `--ayrintili`, `--version`. Özet stdout'a, günlükler ve hata mesajları stderr'e gider.

Bayrakların tamamı, çıkış kodları, günlük kayıtları ve talep dosyasının biçimi: [docs/KOMUT_SATIRI.md](docs/KOMUT_SATIRI.md)

## API özeti

| Uç | İşlev |
|---|---|
| `GET /saglik` | Veritabanına `SELECT 1` gönderir; ulaşılamazsa `503` döner. |
| `GET /talepler` | Talepleri en yeniden eskiye, sayfa sayfa listeler; `durum`, `oncelik`, `etiket`, `ara`, `limit` ve `ayrac` parametrelerini alır. |
| `GET /talepler/ozet` | Her durumdaki talep sayısını verir. |
| `GET /talepler/{talep_id}` | Tek talebi verir; `ETag` başlığında talebin sürümü bulunur. |
| `POST /talepler` | Yeni talep oluşturur. |
| `PATCH /talepler/{talep_id}` | `If-Match`'teki sürüm güncelse durumu, önceliği ya da ikisini değiştirir. |
| `GET /talepler/{talep_id}/yorumlar` | Talebin yorumlarını eklenme sırasıyla listeler. |
| `POST /talepler/{talep_id}/yorumlar` | Talebe yorum ekler. |

Okuma uçları açıktır. `POST` ve `PATCH` uçları `X-API-Anahtari` başlığında sunucudaki `API_ANAHTARI` değerini ister; anahtar ayarlanmamış bir sunucuda yazma tamamen kapalıdır.

Hata kodları, sayfalama, arama yazımı, koşullu istekler ve örnek istekler: [docs/API.md](docs/API.md)

## Ortam değişkenleri

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `PYPI_ZAMAN_ASIMI` | `10` | PyPI isteğinin zaman aşımı, saniye cinsinden. |
| `DATABASE_URL` | yok | API'nin, `talep-yukle`'nin ve `alembic` komutlarının bağlandığı veritabanı. |
| `TEST_DATABASE_URL` | yok | PostgreSQL testlerinin veritabanı. Asıl veritabanını göstermemelidir; şeması her test oturumunda silinip yeniden kurulur. |
| `API_ANAHTARI` | yok | `POST` ve `PATCH` için beklenen `X-API-Anahtari` değeri. |

uv `.env` dosyasını kendiliğinden okumaz; `--env-file .env` ile verilir. `.env` ve `.env.db` Git'e dahil edilmez. Ayrıntılar: [docs/KURULUM.md](docs/KURULUM.md#ortam-değişkenleri)

## Klasör yapısı

```
src/yardim_masasi/
  __init__.py     yardim-masasi komutu: argümanlar, eşzamanlı sorgular, çıkış kodları
  pypi.py         PyPI sorguları ve özet biçimi
  eszamanli.py    sınırlı eşzamanlı toplama ve async yeniden deneme
  araclar.py      senkron yeniden deneme dekoratörü
  model.py        talep modeli, doğrulama ve dosya okuma
  akis.py         satır satır okuma ve JSON Lines üreteçleri
  filtre.py       durum, öncelik, etiket ve açılış zamanı filtreleri
  talepler.py     sayma, sıralama, arama ve talep-ozeti komutu
  depo.py         bellekteki talep deposu
  metin.py        Türkçe metin yardımcıları
  veritabani.py   DATABASE_URL okuma ve talep-yukle komutu
  pg_depo.py      PostgreSQL talep deposu
  sayfa.py        sayfalama ayracı
  sema.py         API gövdeleri ve yanıtları için Pydantic şemaları
  api.py          FastAPI uygulaması
migrations/       Alembic ortamı ve revizyonlar (versions/)
tests/            pytest testleri ve pyright ile denetlenen tip_araclar.py
ornek/            örnek talep dosyaları (.json, .jsonl)
docs/             ayrıntılı belgeler
notes/            günlük çalışma notları
compose.yaml      db, migrate ve api servisleri
Dockerfile        iki aşamalı imaj
pyproject.toml    proje tanımı, bağımlılıklar ve komutların giriş noktaları
uv.lock           kilitlenmiş bağımlılık sürümleri
```

Modüllerin ayrıntılı açıklaması: [docs/MIMARI.md](docs/MIMARI.md)

## Testler

```bash
uv run --locked --env-file .env pytest -q
uv run pyright
```

PostgreSQL testleri için veritabanı kabının açık olması ve test veritabanının bir kez oluşturulması gerekir:

```bash
docker compose exec db createdb -U yardim yardim_masasi_test
```

`--env-file .env` verilmezse `TEST_DATABASE_URL` tanımlı olmaz ve PostgreSQL testleri atlanır; aynı depo testlerinin bellekteki kopyaları ve API testleri Docker kapalıyken de çalışır.

Testlerin ne denetlediği, tip denetimi ve bağımlılık yönetimi: [docs/GELISTIRME.md](docs/GELISTIRME.md)

## Bilinen eksikler

- API anahtarı tek ve herkesin paylaştığı bir değer. Kullanıcı ayrımı yok; bir talebi kimin oluşturduğu ya da değiştirdiği kaydedilmiyor.
- Sayfalar yalnızca ileri gidiyor. Yanıtta toplam talep ya da sayfa sayısı yok.
- Arama yalnızca başlıkta yapılıyor. Türkçe kök bulucu bazı ekli kelimeleri yalın hâlleriyle eşleştiremiyor.
- Kapta tek bir uvicorn süreci çalışıyor. Taban imajlar etiketle seçiliyor, özetle sabitlenmiyor.
- PyPI sorguları için önbellek bulunmuyor.

Tam liste: [docs/BILINEN_SINIRLAMALAR.md](docs/BILINEN_SINIRLAMALAR.md)

## Lisans

Kod [MIT lisansı](LICENSE) ile sunulur.
