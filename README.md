# Yardım Masası

`yardim-masasi`, verilen Python paketlerinin PyPI'da bildirilen güncel sürümünü ve desteklediği Python sürüm aralığını terminalde gösteren küçük bir komut satırı aracıdır. Paketleri kurmadan bilgilerini sorgular.

`talep-ozeti` komutu bir JSON dosyasındaki destek taleplerini durumlarına göre sayar ve kapanmamış talepleri öncelik sırasıyla listeler. `ornek/talepler.json` on iki örnek talep içerir.

Proje aynı zamanda Python yorumlayıcısı, sanal ortam, `uv`, bağımlılık yönetimi ve ortam değişkenleri üzerine bir çalışma örneğidir.

## Gerekenler

- [uv](https://docs.astral.sh/uv/): Python ve proje bağımlılıklarını yönetir.
- Python 3.15: geliştirme sürümü `.python-version` dosyasında seçilidir. `pyproject.toml` en az Python 3.15 ister. Uygun yorumlayıcı yoksa uv, otomatik indirme açıkken onu kurabilir.
- İlk kurulumda paketleri indirmek ve kullanım sırasında PyPI'ya erişmek için internet bağlantısı.

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

## Kod Düzeni

`src/yardim_masasi/` altında:

    model.py      Talep, Durum, Oncelik ve hata sınıfları; dosyayı okuyup her talebi doğrular
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

## Ortam Değişkenleri

İsteğe bağlı yerel ayarlar için, `.env` henüz yoksa örnek dosyayı kopyala:

```bash
cp .env.example .env
```

| Değişken | Varsayılan | Açıklama |
| --- | --- | --- |
| `PYPI_ZAMAN_ASIMI` | `10` | HTTP isteğinin zaman aşımı ayarı, saniye cinsinden. `2.5` gibi ondalık değerler kullanılabilir. |

uv `.env` dosyasını kendiliğinden okumaz; dosyayı açıkça belirt:

```bash
uv run --locked --env-file .env yardim-masasi httpx
```

Dosya oluşturmadan tek komuta değer vermek de mümkündür (Bash):

```bash
PYPI_ZAMAN_ASIMI=2.5 uv run --locked yardim-masasi httpx
```

`.env` Git'e dahil edilmez; paylaşılabilir ayar örnekleri `.env.example` içinde tutulur.

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
pyproject.toml        Proje tanımı, bağımlılıklar ve komutun giriş noktası.
uv.lock               Çözümlenmiş doğrudan ve dolaylı bağımlılıklar.
.python-version       Geliştirmede seçilen Python sürümü.
.env.example          Paylaşılabilir ortam değişkeni örneği.
```

Çalışma bağımlılıkları `httpx` ve `rich`, geliştirme bağımlılıkları `pytest` ve `pyright` olarak tanımlıdır. HTTP isteklerini `httpx` yapar. `rich` bağımlılıklarda bulunur, ancak mevcut çıktı düz `print` ile üretilir.

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
uv run --locked pytest -q
uv run pyright
```

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

## Çalışma Notları ve Git Akışı

[23.10.2026 günlük özeti](notes/daily-summary-23-10-2026.md), Python ve uv ile ilgili öğrenme notlarını içerir.

[27.10.2026 günlük özeti](notes/daily-summary-27-10-2026.md), Python veri tipleri, metin işleme ve talep fonksiyonları üzerine öğrenme notlarını içerir.

[28.10.2026 günlük özeti](notes/daily-summary-28-10-2026.md), sınıflar, talep modeli, sınırda doğrulama ve çıkış kodları üzerine öğrenme notlarını içerir.

[06.11.2026 günlük özeti](notes/daily-summary-06-11-2026.md), parametre türleri,
zamanlı talepler, filtreler, argparse, logging ve testlerle ilgili çalışma
notlarını içerir.

[07.11.2026 günlük özeti](notes/daily-summary-07-11-2026.md), tip denetimi,
generic dekoratörler, asyncio, iptal ve eşzamanlı PyPI sorgularını açıklar.

Değişiklikler yerel çalışma alanında tutulur; kullanıcı açıkça istemeden commit veya GitHub'a push yapılmaz. Commit istendiğinde anlamlı işler ayrı commitlere ayrılır; push için ayrıca kullanıcının talebi gerekir.
