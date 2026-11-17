# Yardım Masası

`yardim-masasi`, verilen Python paketlerinin PyPI'da bildirilen güncel sürümünü ve desteklediği Python sürüm aralığını terminalde gösteren küçük bir komut satırı aracıdır. Paketleri kurmadan bilgilerini sorgular.

`talep-ozeti` komutu bir JSON dosyasındaki destek taleplerini durumlarına göre sayar ve kapanmamış talepleri öncelik sırasıyla listeler. `ornek/talepler.json` on iki örnek talep içerir.

Projenin üçüncü parçası, talepleri PostgreSQL'de saklayıp listeleme, okuma, oluşturma ve güncelleme işlerini HTTP üzerinden sunan bir FastAPI uygulamasıdır. API taleplere yazılan yorumları da tutar, talepleri sayfa sayfa listeler ve başlıklarında arar; veritabanı şeması Alembic migration'larıyla kurulur. Veritabanı, migration'lar ve API tek bir `docker compose up` komutuyla kaplarda çalışır.

Proje aynı zamanda Python yorumlayıcısı, sanal ortam, `uv`, bağımlılık yönetimi ve ortam değişkenleri üzerine bir çalışma örneğidir.

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

## PyPI Sorgusu

`yardim-masasi [-h] [-e N] PAKET [PAKET ...]`, en az bir paket adı ister.
`-e N` veya `--eszamanli N`, aynı anda yürütülen sorguların üst sınırını
belirler; varsayılanı **4** olan bu değer pozitif tam sayı olmalıdır.
`-e 1` sorguları sırayla yürütür; `-e 2` en fazla iki sorguyu birlikte yürütür.

İstekler ortak bir `httpx.AsyncClient` ile yapılır. Sonuçlar bütün işler
tamamlandıktan sonra, yanıtların geliş sırasına göre değil komutta verilen
paket sırasıyla yazılır. Paket özetleri stdout'a, hata mesajları stderr'e
gider; bu iki akışı birleştiren araçların ekrandaki sıralaması tamponlama
nedeniyle farklı görünebilir.

Bağlantı ve zaman aşımı gibi taşıma hataları yarım saniye arayla iki kez
daha denenir; ilk istekle birlikte toplam üç deneme yapılır. HTTP 404 ve
diğer HTTP durum hataları yeniden denenmez. Bulunamayan paket diğer paketlerin
özetlerini engellemez; taşıma hatası son denemede de sürerse kalan işler
iptal edilir ve paket özetleri basılmadan komut hata mesajıyla sonlanır.

| Çıkış kodu | Anlamı |
| --- | --- |
| `0` | Bütün paketler başarıyla sorgulandı veya yardım gösterildi. |
| `1` | Paket bulunamadı (404), başka bir HTTP durum hatası oluştu veya yeniden denemelere rağmen PyPI'a ulaşılamadı. |
| `2` | Kullanım hatası: paket adı eksik, bilinmeyen bayrak veya geçersiz/eksik `-e` değeri. |

Bu ağ ve HTTP hataları hata izi yerine kısa mesajlarla bildirilir. Kullanım
hatalarında `argparse` kullanım özetini ve açıklamayı stderr'e yazar.

## Komut Satırı

`uv run talep-ozeti --help` çıktısının özeti:

```text
talep-ozeti [-h] [--durum {acik,beklemede,kapali}]
           [--oncelik {yuksek,orta,dusuk}] [--etiket ETIKET]
           [--son-gun N] [-v] [--version] [dosya]
```

İsteğe bağlı `dosya`, okunacak `.json` veya `.jsonl` dosyasıdır; verilmezse
çalışma klasörüne göre `ornek/talepler.json` kullanılır.

| Bayrak | İşlev | Örnek komut |
| --- | --- | --- |
| `-h`, `--help` | Yardımı gösterir ve çıkar. | `uv run talep-ozeti -h` veya `uv run talep-ozeti --help` |
| `--durum` | `acik`, `beklemede` veya `kapali` durumunu seçer. | `uv run talep-ozeti --durum kapali` |
| `--oncelik` | `yuksek`, `orta` veya `dusuk` önceliğini seçer. | `uv run talep-ozeti --oncelik yuksek` |
| `--etiket` | Verilen etiketi tam olarak taşıyan talepleri seçer. | `uv run talep-ozeti --etiket hesap` |
| `--son-gun N` | Son N günlük alt zaman sınırını uygular; N pozitif tam sayı olmalıdır. | `uv run talep-ozeti ornek/talepler-zamanli.jsonl --son-gun 10` |
| `-v`, `--ayrintili` | DEBUG günlüklerini açar. | `uv run talep-ozeti -v` veya `uv run talep-ozeti --ayrintili` |
| `--version` | Kurulu paketin sürümünü gösterir ve çıkar. | `uv run talep-ozeti --version` |

Filtreler birlikte uygulanır; örneğin `uv run talep-ozeti --oncelik yuksek --etiket hesap`
iki koşulu da sağlayanları seçer. Sayımlar filtrelenmiş bütün talepleri içerir;
liste, `--durum` verilmedikçe yalnızca kapanmamış talepleri gösterir.
`--durum kapali` kapalı talepleri de listeler. Hiç eşleşme yoksa sayımlar sıfırdır
ve komut başarıyla biter; yardım ve sürüm seçenekleri talep dosyasını okumaz.

| Çıkış kodu | Anlamı | Örnek durum |
| --- | --- | --- |
| `0` | Başarı | Özet, yardım veya sürüm yazıldı. |
| `1` | Talep hatası | Dosya okunamadı ya da bir talep doğrulanamadı. |
| `2` | Kullanım hatası | Bilinmeyen bayrak, geçersiz seçenek değeri, eksik bayrak değeri veya birden fazla dosya verildi. |

Talep hataları tek satırlık mesajla stderr'e yazılır. Kullanım hatalarında
`argparse` kullanım özetini ve hata açıklamasını stderr'e yazar.

## Günlük Kayıtları

`talep-ozeti` için `-v` veya `--ayrintili`, günlük seviyesini DEBUG yapar; dosyadan okunan ve
filtrelerden sonra kalan talep sayıları görünür. Bayrak verilmezse seviye
WARNING'dir. `yeniden_dene` yardımcısı yeniden denenecek hataları WARNING,
son denemedeki hatayı ERROR seviyesinde kaydeder; bu kayıtlar ilgili işlem
çalıştığında oluşur.

`yardim-masasi` artık async istekleri ve `yeniden_dene_async` dekoratörünü
kullanır; PyPI yeniden deneme kayıtları **`yardim_masasi.eszamanli`**
kaydedicisinden gelir. Burada da yeniden denenecek hata WARNING, son hata
ERROR seviyesindedir. Senkron `yeniden_dene` kayıtları ise
`yardim_masasi.araclar` adını kullanmaya devam eder.

Özet stdout'a, günlükler stderr'e gider. Böylece özeti başka bir komuta veya
dosyaya aktarırken tanılama mesajları sonuç verisine karışmaz. Kütüphane
modülleri `logging.getLogger(__name__)` ile kayıt üretir; seviye ve biçimi
`talep-ozeti` girişindeki `logging.basicConfig` belirler.

Bash'te özeti ve günlükleri birlikte ekranda görmek ve dosyaya kaydetmek için:

```bash
set -o pipefail
uv run talep-ozeti ornek/talepler-zamanli.jsonl --son-gun 10 -v 2>&1 | tee talep-ozeti.log
```

`2>&1`, stderr'i stdout'un gittiği yere yönlendirir; `tee` birleşen akışı hem
terminale hem dosyaya yazar. `tee` dosyayı yeniden yazar; ekleme için
`tee -a talep-ozeti.log` kullanılır. `pipefail`, soldaki komut başarısızken
`tee` başarılı diye boru hattının başarılı görünmesini önler; Bash bu ayarla
en sağdaki başarısız komutun çıkış kodunu döndürür.

## Talep Dosyası

Bir JSON listesi (`.json`) ya da her satırında bir talep olan bir JSON Lines dosyası (`.jsonl`). Hangisi olduğu dosyanın uzantısından anlaşılır; `.jsonl` dosyasındaki boş satırlar atlanır. Her talep şu alanları taşır:

    id          sayı
    baslik      metin
    durum       acik, beklemede, kapali
    oncelik     yuksek, orta, dusuk
    etiketler   metin listesi (boş olabilir)
    musteri     e-posta adresi
    acildi      isteğe bağlı, saat dilimi içeren ISO 8601 tarih-saat metni

`id`, `baslik`, `durum`, `oncelik` ve `musteri` zorunlu; `etiketler` yazılmazsa boş sayılır. `id` pozitif bir tam sayıdır ve dosyada bir kez geçer. `musteri` `@` içerir. Fazladan alanlar yok sayılır.

## Zamanlı Talepler

`acildi` alanı, `2026-11-02T09:30:00+03:00` gibi ISO 8601 tarih-saat metnidir.
`+03:00`, UTC'ye göre üç saat ileriyi belirtir; aynı an UTC olarak
`2026-11-02T06:30:00Z` şeklinde de yazılabilir. Saat dilimi zorunludur:
`2026-11-02T09:30:00` gibi ofsetsiz bir değer geçersiz talep sayılır ve komut
`1` koduyla biter. Alan yazılmazsa veya `null` ise modelde `None` olur;
eski talep dosyaları okunmaya devam eder.

[ornek/talepler-zamanli.jsonl](ornek/talepler-zamanli.jsonl), her satırında
`acildi` alanı bulunan toplam on iki örnek talep içerir:

```bash
uv run talep-ozeti ornek/talepler-zamanli.jsonl --son-gun 10
```

`--son-gun 10`, çalıştırma anından on günlük süreyi çıkarıp bir alt sınır
hesaplar; bu sınırdaki ve daha yeni talepleri tutar. Bu bir takvim günü
başlangıcı hesabı değildir. Zamanı olmayan talepler bu filtrede elenir;
zaman filtresi verilmezse korunur. Mevcut filtre gelecekteki tarihlere üst
sınır koymaz. Örnekteki tarihler sabit olduğu için aynı komutun sonucu
çalıştırıldığı güne göre değişir; bütün tarihler eskidiğinde sıfır sayımları
normaldir.

## Veritabanı

PostgreSQL 18, `compose.yaml` ile bir Docker kabında çalışır ve yalnızca bu bilgisayardan, `127.0.0.1:5434` adresinden erişilebilir. Kabın kullanıcı adı, parolası ve ilk veritabanı `.env.db` dosyasından okunur:

```bash
cp .env.db.example .env.db
docker compose up -d
docker compose ps          # db servisi "healthy" görünmeli
```

PostgreSQL ilk açılışta yalnızca `POSTGRES_DB` içindeki `yardim_masasi` veritabanını oluşturur. Testlerin kullandığı ayrı veritabanını bir kez elle açmak gerekir:

```bash
docker compose exec db createdb -U yardim yardim_masasi_test
```

Şema, `migrations/versions/` altındaki Alembic revizyonlarıyla kurulur. Asıl veritabanını en son revizyona getirmek için:

```bash
uv run --env-file .env alembic upgrade head
```

Alembic bağlanacağı adresi `alembic.ini`'den değil, `DATABASE_URL`'den alır. Test veritabanına elle `upgrade` gerekmez; testler şemayı kendileri kurar (bkz. [Testler](#testler)).

Revizyonlar:

    0001  talepler tablosu, kısıtları ve durum indeksi
    0002  talepler.surum sütunu (varsayılan 1, surum >= 1 kısıtı)
    0003  yorumlar tablosu; talep_id talepler.id'ye ON DELETE CASCADE ile bağlı
    0004  talepler üzerinde (acildi, id) indeksi; sayfalamayı hızlandırır
    0005  talepler.arama sütunu (to_tsvector('turkish', baslik), STORED) ve GIN indeksi

Sık kullanılan komutlar (hepsi `uv run --env-file .env alembic ...` biçiminde):

| Komut | Etkisi |
| --- | --- |
| `alembic current` | Veritabanının hangi revizyonda olduğunu gösterir, ör. `0003 (head)`. |
| `alembic history` | Revizyon zincirini listeler. |
| `alembic upgrade head` | Bekleyen bütün revizyonları sırayla uygular. |
| `alembic downgrade -1` | Son revizyonu geri alır; `downgrade` içindeki komutları çalıştırır ve veri kaybettirebilir. |
| `alembic upgrade head --sql` | Veritabanına bağlanmadan, uygulanacak SQL'i ekrana yazar. |

Hangi revizyonun uygulandığı veritabanındaki `alembic_version` tablosunda tutulur. Tablosu daha önce `sql/001_talepler.sql` ile elle kurulmuş bir veritabanında bu tablo yoktur; `upgrade head` 0001'i baştan çalıştırmaya kalkar ve `relation "talepler" already exists` hatasıyla durur. Böyle bir veritabanında önce şemanın zaten 0001'de olduğu kaydedilir, sonra kalan revizyonlar uygulanır:

```bash
uv run --env-file .env alembic stamp 0001
uv run --env-file .env alembic upgrade head
```

`stamp` yalnızca `alembic_version`'a yazar, şemaya dokunmaz. Yeni bir revizyon, sıradaki numarayla açılır ve `upgrade`/`downgrade` fonksiyonları elle yazılır:

```bash
uv run alembic revision --rev-id 0006 -m "kisa aciklama"
```

Örnek talepleri asıl veritabanına `talep-yukle` yükler. Dosya verilmezse `ornek/talepler-zamanli.jsonl` okunur:

```bash
uv run --env-file .env talep-yukle
uv run --env-file .env talep-yukle ornek/talepler.json
```

`talep-yukle` dosyadaki numaraları korur ve bütün talepleri tek işlemde ekler; bir hata olursa hiçbiri eklenmez. Tabloda zaten talep varsa hiçbir şey eklemez, `talep-yukle: tablo boş değil (12 talep var)` gibi bir mesajı stderr'e yazar ve `1` koduyla biter. Ekleme bittikten sonra `id` sütununun numara sayacını tablodaki en büyük numaraya ayarlar; böylece API ile oluşturulan ilk talep bir sonraki numarayı alır ve var olan bir numarayla çakışmaz.

Tabloyu boşaltıp sayacı sıfırlamak ve örnekleri yeniden yüklemek için:

```bash
docker compose exec db psql -U yardim -d yardim_masasi -c "TRUNCATE talepler RESTART IDENTITY CASCADE"
uv run --env-file .env talep-yukle
```

`CASCADE` gereklidir: 0003'ten sonra `yorumlar` tablosu `talepler`'e yabancı anahtarla bağlı olduğu için `CASCADE`'siz komut `cannot truncate a table referenced in a foreign key constraint` hatası verir. `CASCADE` yorumları da siler.

`docker compose down` kabı durdurur, veriler `db-data` biriminde kalır. `docker compose down -v` birimi de siler; bir sonraki `up` boş bir veritabanıyla başlar ve test veritabanını açma ile `alembic upgrade head` adımları yeniden gerekir.

## API

```bash
uv run --env-file .env fastapi dev src/yardim_masasi/api.py
```

Sunucu `http://127.0.0.1:8000` adresinde açılır ve kod değiştikçe kendini yeniden başlatır. Başlarken bağlantı havuzunu açar; `DATABASE_URL` tanımlı değilse ya da veritabanına beş saniye içinde bağlanılamazsa başlamaz. `http://127.0.0.1:8000/docs`, uçları tarayıcıdan denemeye yarayan otomatik belgeyi gösterir.

| Uç | İşlev | Başarı | Hata kodları |
| --- | --- | --- | --- |
| `GET /saglik` | Veritabanına `SELECT 1` gönderir; havuzdan bağlantı için en çok 2 saniye bekler. | `200` `{"durum": "ok"}` | `503` `{"durum": "veritabanına ulaşılamıyor"}`, veritabanına ulaşılamazsa |
| `GET /talepler` | Talepleri en yeniden eskiye, sayfa sayfa listeler; `durum`, `oncelik` ve `etiket` ile süzer, `?ara=` ile başlıkta arar; `?limit=` sayfa boyunu, `?ayrac=` sonraki sayfayı seçer. | `200` | `400` bozuk ayraç, `422` bilinmeyen durum veya öncelik, geçersiz `limit` ya da `ara` |
| `GET /talepler/ozet` | Her durumdaki talep sayısını verir; talebi olmayan durum `0` görünür. | `200` | — |
| `GET /talepler/{talep_id}` | Tek talebi verir; `ETag` başlığında talebin sürümü bulunur. `If-None-Match` sürümle eşleşirse gövdesiz `304` döner. | `200`, `304` | `404` talep yok, `422` numara pozitif tam sayı değil |
| `POST /talepler` | Yeni talep oluşturur; durum her zaman `acik`, öncelik verilmezse `orta` olur. | `201` | `401` anahtar, `422` geçersiz gövde |
| `PATCH /talepler/{talep_id}` | `If-Match`'teki sürüm güncelse durumu, önceliği ya da ikisini değiştirir. | `200`, yeni `ETag` | `401` anahtar, `428` `If-Match` yok, `400` biçimsiz `If-Match`, `422` geçersiz veya boş gövde, `404` talep yok, `412` sürüm eski |
| `GET /talepler/{talep_id}/yorumlar` | Talebin yorumlarını eklenme sırasıyla listeler. | `200` | `404` talep yok |
| `POST /talepler/{talep_id}/yorumlar` | Talebe `yazan` ve `metin` ile yorum ekler. | `201` | `401` anahtar, `422` geçersiz gövde, `404` talep yok |

### Liste ve Sayfalar

`GET /talepler` bir liste değil, tek bir sayfa döndürür:

```json
{"talepler": [{"id": 12, "baslik": "...", "surum": 1}, ...], "sonraki": "eyJhIjoiMjAyNi0xMC0zMFQwNjowMDowMCswMDowMCIsImkiOjEwfQ"}
```

Talepler en yeniden eskiye, yani açılış zamanına (`acildi`) göre azalan sırada gelir; aynı anda açılmış talepler arasında büyük numara önce gelir. `limit` bir sayfadaki talep sayısıdır: varsayılanı `20`, alabileceği değerler `1`–`100`; aralık dışındaki ya da sayı olmayan bir değer `422` alır.

`sonraki`, sonraki sayfanın nereden başlayacağını gösteren bir ayraçtır; son sayfada `null` olur. Ayraç, istemcinin okuması ya da değiştirmesi için değil, olduğu gibi `?ayrac=` ile geri yollanması için verilir; aynı `durum`, `oncelik`, `etiket`, `ara` ve `limit` değerleriyle birlikte gönderilir. Bu API'nin vermediği ya da bozulmuş bir ayraç `400` alır.

Ayraç bir sayfa numarası değil, sayfanın son talebinin `(acildi, id)` çiftidir; sonraki sayfa bu çiftten küçük olanlarla başlar. Bu yüzden iki sayfa arasında yeni bir talep açılsa da sayfalar kaymaz: hiçbir talep iki kez gelmez, hiçbiri atlanmaz. Yeni talep, listeyi baştan okuyan bir sonraki istekte görünür.

```bash
curl "http://127.0.0.1:8000/talepler?limit=3"
curl "http://127.0.0.1:8000/talepler?limit=3&ayrac=eyJhIjoiMjAyNi0xMC0zMFQwNjowMDowMCswMDowMCIsImkiOjEwfQ"
```

On iki örnek talepte ilk komut 12, 11 ve 10 numaralı talepleri, ikincisi 9, 8 ve 7'yi verir.

### Arama

`ara`, talep başlıklarında PostgreSQL'in Türkçe tam metin aramasıyla arar. Kelimeler köklerine indirilir ve büyük/küçük harfe bakılmaz; `kargom` "Kargo" geçen başlığı, `şifremi` "Şifre" geçen başlığı bulur.

| Yazım | Anlamı |
| --- | --- |
| `kargo numarası` | Boşlukla ayrılan kelimelerin hepsi başlıkta geçmeli. |
| `kargo or şifre` | Kelimelerden biri geçmesi yeter. |
| `kargo -takip` | `takip` geçen başlıklar elenir. |
| `"takip numarası"` | Tırnak içindeki kelimeler bu sırayla, yan yana geçmeli. |

`ve`, `ile`, `için` gibi durak kelimeleri aramaya katılmaz; yalnızca durak kelimesinden oluşan bir arama hata vermez, boş liste döner. `ara` 2–100 karakter olmalıdır; dışındaki değerler `422` alır.

Sonuçlar alakaya göre sıralanmaz; listeyle aynı sırada, en yeniden eskiye gelir ve aynı ayraçla sayfalanır. `ara` öteki süzgeçlerle birlikte kullanılabilir.

```bash
curl "http://127.0.0.1:8000/talepler?ara=fatura"
```

### Sürüm ve Koşullu İstekler

Her talebin bir `surum` sütunu vardır; yeni talep `1` ile başlar ve her başarılı `PATCH` onu bir artırır. `GET /talepler/{talep_id}` bu sürümü tırnak içinde `ETag` başlığında da verir, ör. `ETag: "3"`.

`PATCH`, istemcinin en son okuduğu sürümü `If-Match` başlığında ister. Sürüm kontrolü ile yazma tek bir `UPDATE ... WHERE id = ... AND surum = ...` komutunda yapılır; iki istemci aynı sürümle aynı anda güncellemeye kalkarsa yalnız biri yazar, diğeri `412` alır. Böylece birinin değişikliği farkında olunmadan ezilmez.

| Durum | Yanıt |
| --- | --- |
| `If-Match` yok | `428 Precondition Required`; önce talebi `GET` ile okumak gerekir. |
| `If-Match` tırnaklı tek bir pozitif sayı değil (`1`, `W/"1"`, `*`, `"abc"`, `"0"`, birden çok etiket) | `400 Bad Request` |
| Sürüm güncel değil | `412 Precondition Failed`; hiçbir şey yazılmaz, yanıtın `ETag` başlığı güncel sürümü gösterir. |
| Sürüm güncel | `200 OK`; gövde güncellenen talep, `ETag` yeni sürüm. |

Denetimler şu sırayla yapılır: `401` (API anahtarı), `428`/`400` (`If-Match`), `422` (gövde), `404` (talep), `412` (sürüm). Örneğin anahtarsız ve `If-Match`'siz bir istek `401` alır.

`GET /talepler/{talep_id}`, `If-None-Match` başlığını da okur. İstemci elindeki `ETag`'i bu başlıkla gönderir; talep o sürümdeyse yanıt gövdesiz `304 Not Modified` ve aynı `ETag`'dir, istemci elindeki kopyayı kullanır. Sürüm değişmişse her zamanki gibi `200`, güncel gövde ve yeni `ETag` döner.

Karşılaştırma zayıftır: `W/"3"` ile `"3"` aynı sayılır. Başlık virgülle ayrılmış birden çok etiket taşıyabilir; biri tutarsa `304` döner. `*` her etikete uyar. Talep yoksa başlık ne olursa olsun `404` döner.

```bash
curl -i http://127.0.0.1:8000/talepler/4 -H 'If-None-Match: "1"'   # 304 Not Modified, ETag: "1"
```

### Anahtar ve Gövde

Okuma uçları açıktır. `POST` ve `PATCH` uçları, `X-API-Anahtari` başlığında sunucudaki `API_ANAHTARI` değerinin aynısını ister. Başlık yoksa, değer yanlışsa ya da sunucuda `API_ANAHTARI` hiç tanımlı değilse istek `401` alır ve hiçbir şey değişmez; anahtar ayarlanmamış bir sunucuda yazma tamamen kapalıdır.

Gövdeler Pydantic şemalarıyla doğrulanır. Başlık boşlukları temizlendikten sonra 3–200 karakter, `musteri` tek `@` içeren bir adres, her etiket 1–30 karakter olmalıdır. Şemada bulunmayan bir alan, örneğin oluştururken gönderilen `durum` ya da `id`, sessizce yok sayılmaz; istek `422` ve `extra_forbidden` hatası alır.

```bash
curl -i -X POST http://127.0.0.1:8000/talepler \
  -H "Content-Type: application/json" \
  -H "X-API-Anahtari: gelistirme-anahtari" \
  -d '{"baslik": "Fatura indirilemiyor", "musteri": "ali@example.com", "oncelik": "yuksek", "etiketler": ["fatura"]}'
```

Yanıt `201 Created` ve veritabanının verdiği numara, durum, açılış zamanı ve `surum: 1` ile oluşan talebin JSON'udur.

```bash
curl -i http://127.0.0.1:8000/talepler/4          # ETag: "1"
curl -i -X PATCH http://127.0.0.1:8000/talepler/4 \
  -H "Content-Type: application/json" \
  -H "X-API-Anahtari: gelistirme-anahtari" \
  -H 'If-Match: "1"' \
  -d '{"durum": "kapali"}'
```

İlk `PATCH` `200` ve `ETag: "2"` döner; aynı komut ikinci kez gönderilirse sürüm artık `2` olduğu için `412` alır.

### Yorumlar

Yorumlar `yorumlar` tablosunda tutulur ve `talep_id` ile talebe bağlıdır. Gövde yalnızca `yazan` (1–60 karakter) ve `metin` (1–2000 karakter) alır; boşluklar temizlenir, `talep_id` gibi fazladan bir alan `422` alır. Yanıtta `id`, `talep_id`, `yazan`, `metin` ve veritabanının verdiği `yazildi` zamanı bulunur. Yorum eklemek talebin sürümünü ve `ETag`'ini değiştirmez. Silinen bir talebin yorumları da silinir.

```bash
curl -i -X POST http://127.0.0.1:8000/talepler/4/yorumlar \
  -H "Content-Type: application/json" \
  -H "X-API-Anahtari: gelistirme-anahtari" \
  -d '{"yazan": "ayse", "metin": "Müşteriyi aradım."}'
```

## Kapta Çalıştırma

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

## Tip Denetimi

```bash
uv run pyright
```

`pyproject.toml`, `src` ve `tests` dizinlerini denetime dahil eder.
`src/yardim_masasi/araclar.py`, `src/yardim_masasi/eszamanli.py` ve
`tests/tip_araclar.py`, başlarındaki `# pyright: strict` ile strict
denetlenir. Diğer dosyalar pyright'ın varsayılan standard modunu kullanır.
Tip ipuçları çalışma anında girdileri doğrulamaz; pyright kodu çalıştırmadan
tip uyumsuzluklarını arar.

`tests/tip_araclar.py`, `assert_type` ile dekoratörün dönüş tipini ve kasıtlı
hatalı çağrılarla parametre imzasını denetler. Dosya adı pytest'in varsayılan
`test_*.py` veya `*_test.py` kalıplarına uymaz; bu nedenle pytest tarafından
toplanmaz. Pyright ise `tests` kapsamındaki bu dosyayı statik olarak inceler;
içindeki hatalı çağrıları çalıştırmaz.

`reportUnnecessaryTypeIgnoreComment = "error"`, artık bir tip hatasını
bastırmayan gereksiz `ignore` yorumlarını hata sayar. Böylece dekoratörün
tip imzası zayıflayıp yanlış çağrılar kabul edilmeye başlarsa ilgili
`pyright: ignore[...]` satırları denetimi başarısız kılar; eski bastırma
yorumlarının sessizce kalması da önlenir.

## Testler

```bash
uv run --locked --env-file .env pytest -q
uv run pyright
```

`--env-file .env` verilmezse `TEST_DATABASE_URL` tanımlı olmaz; `test_depo_sozlesme.py` içindeki `[pg]` testleri ve `test_gocler.py` atlanır, çıktıda `skipped` olarak görünürler. Aynı depo testlerinin `[bellek]` kopyaları yine çalışır. PostgreSQL testleri için veritabanı kabının açık ve `yardim_masasi_test` veritabanının oluşturulmuş olması gerekir. Kap kapalıyken `--env-file .env` ile çalıştırılırsa bu testler atlanmaz, bağlantı hatasıyla `error` olur.

Test veritabanına elle `alembic upgrade head` gerekmez. `conftest.py`'deki oturum kapsamlı `test_adresi` fikstürü, test oturumunun başında bir kez `public` şemasını silip yeniden açar ve `command.upgrade(..., "head")` ile bütün migration'ları uygular. Depo testleri her testten önce `TRUNCATE talepler RESTART IDENTITY CASCADE` ile tabloları boşaltır.

Testler `alembic.ini`'yi okumaz: `alembic_ayari` yalnızca `script_location`'ı ve `TEST_DATABASE_URL`'i içeren bir `Config` nesnesi kurar. Böylece `migrations/env.py` adresi `DATABASE_URL`'den almaz ve testler yanlışlıkla asıl veritabanına migration uygulamaz; `alembic.ini`'deki günlük ayarları da pytest'in günlük yakalamasına karışmaz.

`test_gocler.py` migration zincirini denetler: veritabanının en son revizyonda olduğunu, bütün revizyonların `base`'e kadar geri alınıp yeniden kurulabildiğini ve her revizyonun tek tek `upgrade`, `downgrade -1`, yeniden `upgrade` yapılabildiğini. Böylece yazılmayı unutulmuş ya da yanlış bir `downgrade` yakalanır.

`test_depo_sozlesme.py`, aynı sözleşme testlerini hem `BellekDeposu` hem `PgTalepDeposu` üzerinde çalıştırarak iki deponun aynı davrandığını doğrular. Arama testleri ise yalnızca PostgreSQL'de koşar: kök bulma, durak kelimeleri, `or`, `-kelime` ve tırnaklı ifade PostgreSQL'in Türkçe sözlüğünden ve `websearch_to_tsquery`'den gelir. Bellek deposundaki arama yalnızca kelimelerin başlıkta geçip geçmediğine bakan kaba bir taklittir; aynı testleri ona koşturmak PostgreSQL'i değil taklidi sınardı.

`test_sayfa.py` veritabanı kullanmaz: ayracın yazılıp okunduğunda aynı kaldığını, saat dilimini koruduğunu, adreste kaçışsız kullanılabildiğini ve bozuk ya da değiştirilmiş metinlerin `GecersizAyrac` ile reddedildiğini denetler. `test_api.py` veritabanı kullanmaz: `TestClient` lifespan'ı çalıştırmadığı için bağlantı havuzu açılmaz ve `app.dependency_overrides` ile `depo_al` yerine bellek deposu verilir. Bu testler Docker kapalıyken de geçer.

`test_saglik.py` de veritabanı kullanmaz. `tests/sahte_havuz.py`'deki `SahteHavuz`, bağlantı havuzunun `connection(timeout=...)` metodunu taklit eder: hata verilmezse sorguyu kaydeden bir `SahteBaglanti` verir; `bekleme_hatasi` havuzun bağlantı veremediği durumu, `sorgu_hatasi` sorgu sırasında kopan bağlantıyı taklit eder. Testler `monkeypatch` ile `app.state.havuz` yerine bu sahte havuzu koyar ve `/saglik`'in veritabanı cevap verince `200` ile `SELECT 1` gönderdiğini, havuz bekletince ve bağlantı kopunca `503` döndüğünü, havuzdan en çok 2 saniye bağlantı beklediğini ve `OperationalError` olmayan bir hatayı yutmadığını denetler.

Testler metin yardımcılarını, talep modelini, zaman doğrulamasını, depoyu, JSONL
akışını, filtreleri ve komutun çıktı/çıkış kodlarını kontrol eder. PyPI yeniden
deneme testleri gerçek ağ isteği yerine sahte yanıtlar ve taşıma hataları kullanır.

## Bağımlılık Yönetimi

| Komut | Etkisi |
| --- | --- |
| `uv add paket` | Çalışma bağımlılığı ekler; proje tanımını, kilidi ve ortamı günceller. |
| `uv add --dev paket` | Geliştirme bağımlılığı ekler. |
| `uv remove paket` | Bağımlılığı kaldırır; kilidi ve ortamı günceller. |
| `uv tree` | Projenin bağımlılık ağacını gösterir. |
| `uv tree --outdated` | Bağımlılık ağacında daha yeni sürümü bulunan paketleri gösterir. |
| `uv lock --upgrade-package paket` | Seçili paketi mevcut kısıtlar içinde yeniden çözümler; gereken dolaylı bağımlılıklar da değişebilir. |
| `uv sync --locked` | Kilit dosyasındaki sürümleri sanal ortama uygular. |

`pyproject.toml` kabul edilen sürüm aralıklarını, `uv.lock` ise seçilmiş kesin sürümleri kaydeder. Örneğin `httpx>=0.28.1` bir alt sınırdır; üst sınır içermez. `uv lock --upgrade-package` sonrasında kurulu ortamı güncellemek için `uv sync --locked`, doğrulamak için test komutu çalıştırılır.

## Bilinen Sınırlamalar

- `yardim-masasi` günlük ayarı yapmaz. Başka bir günlük yapılandırması yoksa yeniden deneme uyarıları ve son hata, logging'in yedek işleyicisiyle stderr'e zaman, seviye ve kaydedici adı olmadan çıplak mesaj olarak yazılır.
- Büyük paket listelerinde bütün sonuçlar beklendiğinden toplam süre en yavaş yanıta da bağlıdır. Eşzamanlılık sınırı yüzünden sırada bekleyen işler ve yeniden denemeler bu süreyi uzatır; hızlı biten paketler hemen gösterilmez.
- `PYPI_ZAMAN_ASIMI` sayıya çevrilemiyorsa `ValueError` oluşur. Değer aralığı için ayrıca doğrulama yapılmaz.
- PyPI sorguları için önbellek bulunmaz.
- Bağımlılıklar için otomatik güvenlik açığı taraması yapılandırılmamıştır.
- Varsayılan `ornek/talepler.json` yolu komutun çalıştırıldığı klasöre göredir; proje kökünden başka bir klasörde "dosya bulunamadı" der.
- Talep dosyası UTF-8 değilse düzgün bir mesaj yok; Python'un hata izi basılır.
- API çalışırken veritabanı kapanırsa havuzdaki kopuk bağlantıyı alan ilk istek hemen hata alır. Sonraki isteklerde yalnızca `/saglik` en çok 2 saniye bekleyip `503` döner; öbür uçlar havuzun 30 saniyelik zaman aşımına kadar bekler ve sonra `500` alır. Veritabanı geri geldiğinde havuzun yeniden bağlanma süresi sabit değildir; istekler birkaç saniye daha hata alabilir.
- Kapta tek bir uvicorn süreci çalışıyor; birden çok işçi ya da kopya yok.
- `migrate` her `docker compose up`'ta çalışıyor. Aynı veritabanına iki yerden aynı anda `up` yapılırsa migration'lar birbiriyle yarışabilir.
- Taban imajlar (`python:3.15-slim`, `ghcr.io/astral-sh/uv:0.13.7`, `postgres:18-alpine`) etiketle seçiliyor, özetle (`@sha256:...`) sabitlenmiyor; aynı etiket zamanla başka bir imajı gösterebilir. İmaj güvenlik açıklarına karşı taranmıyor.
- API anahtarı tek ve herkesin paylaştığı bir değer. Kullanıcı ayrımı yok; bir talebi kimin oluşturduğu ya da değiştirdiği kaydedilmiyor. Anahtarı değiştirmek sunucuyu yeni ortam değişkeniyle yeniden başlatmayı gerektiriyor.
- Migration'lar elle yazılıyor. Tablolar SQLAlchemy modeliyle tanımlanmadığı için `alembic revision --autogenerate` kullanılamıyor; şema ile revizyonların uyumunu yalnızca testler denetliyor.
- `If-Match` yalnızca tek ve tırnaklı bir sürüm kabul ediyor. `*`, zayıf etiket (`W/"1"`) ve virgülle ayrılmış birden çok etiket standartta geçerli olsa da `400` alıyor.
- Yorumlar düzenlenemiyor ve silinemiyor. `yazan` alanı istemcinin yazdığı serbest bir metin; API anahtarı ortak olduğu için yorumu gerçekten kimin yazdığı doğrulanmıyor.
- Sayfalar yalnızca ileri gidiyor: önceki sayfaya dönmek ya da belli bir sayfaya atlamak için ayraç yok. Yanıtta toplam talep ya da sayfa sayısı da yok.
- Arama yalnızca başlıkta yapılıyor; yorumlar ve etiketler aranmıyor. Sonuçlar alakaya göre değil, en yeniden eskiye sıralanıyor.
- Türkçe kök bulucu bazı ekli kelimeleri yalın hâlleriyle eşleştiremiyor: `fatura` ile `faturada` (`fatur` / `fatura`), `numara` ile `numarası` (`numar` / `numaras`), `iade` ile `iadem` (`ia` / `iade`) farklı köklere iniyor, biri ötekini bulmuyor. Yazım hatalarına tolerans yok; `fatüra` hiçbir şey bulmaz.
- Büyük `I` harfi Türkçe kurala göre `ı`'ya değil `i`'ye küçültülüyor: `IŞIKLI` `işikli` olarak saklanıyor, bu yüzden `ışıklı` aramasıyla bulunmuyor.

## Çalışma Notları ve Git Akışı

[23.10.2026 günlük özeti](notes/daily-summary-23-10-2026.md), Python ve uv ile ilgili öğrenme notlarını içerir.

[27.10.2026 günlük özeti](notes/daily-summary-27-10-2026.md), Python veri tipleri, metin işleme ve talep fonksiyonları üzerine öğrenme notlarını içerir.

[28.10.2026 günlük özeti](notes/daily-summary-28-10-2026.md), sınıflar, talep modeli, sınırda doğrulama ve çıkış kodları üzerine öğrenme notlarını içerir.

[06.11.2026 günlük özeti](notes/daily-summary-06-11-2026.md), parametre türleri,
zamanlı talepler, filtreler, argparse, logging ve testlerle ilgili çalışma
notlarını içerir.

[07.11.2026 günlük özeti](notes/daily-summary-07-11-2026.md), tip denetimi,
generic dekoratörler, asyncio, iptal ve eşzamanlı PyPI sorgularını açıklar.

[09.11.2026 günlük özeti](notes/daily-summary-09-11-2026.md), PostgreSQL kabı,
psycopg, bağlantı havuzu, Pydantic şemaları, FastAPI uçları ve API testlerini anlatır.

[10.11.2026 günlük özeti](notes/daily-summary-10-11-2026.md), Alembic migration'ları,
sürüm kontrollü güncelleme, ETag/If-Match ve yorumları anlatır.

Değişiklikler yerel çalışma alanında tutulur; kullanıcı açıkça istemeden commit veya GitHub'a push yapılmaz. Commit istendiğinde anlamlı işler ayrı commitlere ayrılır; push için ayrıca kullanıcının talebi gerekir.
