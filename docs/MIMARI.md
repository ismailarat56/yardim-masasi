[← README'ye dön](../README.tr.md)

# Mimari

## Genel Bakış

`yardim-masasi`, verilen Python paketlerinin PyPI'da bildirilen güncel sürümünü ve desteklediği Python sürüm aralığını terminalde gösteren küçük bir komut satırı aracıdır. Paketleri kurmadan bilgilerini sorgular.

`talep-ozeti` komutu bir JSON dosyasındaki destek taleplerini durumlarına göre sayar ve kapanmamış talepleri öncelik sırasıyla listeler. `ornek/talepler.json` on iki örnek talep içerir.

Projenin üçüncü parçası, talepleri PostgreSQL'de saklayıp listeleme, okuma, oluşturma ve güncelleme işlerini HTTP üzerinden sunan bir FastAPI uygulamasıdır. API taleplere yazılan yorumları da tutar, talepleri sayfa sayfa listeler ve başlıklarında arar; veritabanı şeması Alembic migration'larıyla kurulur. Veritabanı, migration'lar ve API tek bir `docker compose up` komutuyla kaplarda çalışır.

Proje aynı zamanda Python yorumlayıcısı, sanal ortam, `uv`, bağımlılık yönetimi ve ortam değişkenleri üzerine bir çalışma örneğidir.

## Kod Düzeni

`src/yardim_masasi/` altında:

    model.py      Talep (surum alanıyla), Yorum, Durum, Oncelik, SurumCakismasi ve hata sınıfları; dosyayı okuyup her talebi doğrular
    akis.py       üreteçler: satır satır okuma, JSON Lines, parçalara bölme
    araclar.py    ParamSpec ile çağrı imzasını koruyan senkron yeniden_dene dekoratörü
    eszamanli.py  Semaphore ve TaskGroup ile sinirli_topla; yeniden_dene_async dekoratörü
    depo.py       TalepDeposu: talepleri numarasıyla, eklendikleri sırayla tutar
    filtre.py     durum, öncelik, etiket ve açılış zamanına göre filtreleme
    talepler.py   sayma, sıralama ve arama fonksiyonları; talep-ozeti komutu
    metin.py      Türkçe metin yardımcıları
    pypi.py       senkron/async paket sorguları, sınırlı eşzamanlı toplama ve özet biçimi
    __init__.py   yardim-masasi: argümanlar, eşzamanlı sorgular ve çıkış kodları
    __main__.py   python -m yardim_masasi için
    veritabani.py DATABASE_URL okuma; örnekleri yükleyip numara sayacını ayarlayan talep-yukle komutu
    sayfa.py      Ayrac (acildi, id), Sayfa ve GecersizAyrac; ayracı opak bir metne yazan ayrac_yaz ve geri okuyan ayrac_oku
    pg_depo.py    PgTalepDeposu: getir, ekle, ayraçla sayfa sayfa ve tam metin aramayla listele, sürüm kontrollü güncelle, durum sayıları, yorum ekle ve yorumlar
    sema.py       API gövdeleri ve yanıtları için Pydantic şemaları: TalepOlustur, TalepGuncelle, TalepCevap, YorumOlustur, YorumCevap
    api.py        FastAPI uygulaması: lifespan ile bağlantı havuzu, sekiz uç, API anahtarı, sayfalı liste ve arama, ETag, If-Match ve If-None-Match denetimi

Proje kökünde (`sql/` klasörü artık yok; şema migration'larda):

    alembic.ini           Alembic ayarları: migrations/ klasörü ve günlük biçimi; veritabanı adresi burada değil
    migrations/env.py     adresi DATABASE_URL'den alır; --sql ile çevrimdışı, normalde tek işlemde çalışır
    migrations/versions/  0001 talepler, 0002 surum sütunu, 0003 yorumlar revizyonları
    compose.yaml          db (PostgreSQL 18, 127.0.0.1:5434, db-data birimi, sağlık denetimi), tek seferlik migrate ve sağlık kontrollü api (127.0.0.1:8000) servisleri
    Dockerfile            iki aşamalı imaj: kur bağımlılıkları uv ile kurar; calis yalnızca /app'i alır ve uygulama kullanıcısıyla çalışır
    .dockerignore         .venv, .env, .env.db, .git, __pycache__ ve .pytest_cache'i derleme bağlamının dışında tutar

## Proje Yapısı

```text
src/yardim_masasi/
    __init__.py       PyPI komutu; eşzamanlı sorguların sonuçlarını giriş sırasıyla yazar.
    pypi.py           Senkron/async HTTP istekleri, zaman aşımı ve çıktı biçimi.
    araclar.py        Tip imzasını koruyan senkron yeniden deneme dekoratörü.
    eszamanli.py      Sınırlı eşzamanlı toplama ve async yeniden deneme.
    metin.py          Türkçe harf dönüşümü, etiket temizleme ve metin yardımcıları.
    model.py          Talep modeli, veri doğrulama ve dosya okuma hataları.
    talepler.py       Talep filtreleme, sıralama, arama ve özet komutu.
    filtre.py         Birleşik filtreler ve dışarıdan verilebilen referans zaman.
    veritabani.py     Bağlantı adresi ve talep-yukle komutu.
    pg_depo.py        PostgreSQL talep deposu.
    sema.py           API istek ve yanıt şemaları.
    api.py            FastAPI uygulaması, uçlar, ETag ve If-Match.
migrations/           Alembic ortamı (env.py) ve revizyonlar (versions/).
alembic.ini           Alembic ayar dosyası.
tests/conftest.py      anyio_backend ayarı; test veritabanının şemasını migration'larla kuran fikstür.
tests/test_gocler.py   Migration zincirinin geri alınıp yeniden uygulanabildiğini denetler.
tests/sahte_depo.py    PgTalepDeposu ile aynı sözleşmeyi uygulayan bellek deposu.
tests/test_depo_sozlesme.py Aynı depo testlerini bellekte ve PostgreSQL'de koşturur.
tests/test_api.py      Uçların durum kodu, doğrulama, anahtar, If-Match ve yorum testleri.
tests/test_pypi.py     Özet biçimi ve ortam değişkeni testleri.
tests/test_pypi_async.py Eşzamanlı PyPI, sıralama ve hata davranışı testleri.
tests/test_eszamanli.py Eşzamanlılık sınırı, iptal ve async yeniden deneme testleri.
tests/test_cli.py      PyPI komutunun çıktı ve çıkış kodu testleri.
tests/tip_araclar.py   pyright ile dekoratör imzasının statik denetimi.
tests/test_metin.py    Türkçe metin yardımcılarının testleri.
tests/test_talepler.py Talep işlemlerinin testleri.
tests/test_model.py    Talep modeli ve dosya doğrulama testleri.
tests/test_komut.py    Özet komutunun çıktı ve hata akışı testleri.
ornek/talepler.json    On iki örnek destek talebi.
ornek/talepler-zamanli.jsonl Açılış zamanı içeren on iki örnek talep.
notes/                Günlük öğrenme ve çalışma notları.
compose.yaml          PostgreSQL kabının tanımı.
pyproject.toml        Proje tanımı, bağımlılıklar ve komutun giriş noktası.
uv.lock               Çözümlenmiş doğrudan ve dolaylı bağımlılıklar.
.python-version       Geliştirmede seçilen Python sürümü.
.env.example          Paylaşılabilir ortam değişkeni örneği.
.env.db.example       PostgreSQL kabı için örnek ayarlar.
```

Çalışma bağımlılıkları `alembic`, `httpx`, `rich`, `fastapi[standard]`, `psycopg[binary]` ve `psycopg-pool`; geliştirme bağımlılıkları `pytest` ve `pyright` olarak tanımlıdır. HTTP isteklerini `httpx` yapar. `rich` bağımlılıklarda bulunur, ancak mevcut çıktı düz `print` ile üretilir.
