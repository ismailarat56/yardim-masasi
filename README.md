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

`uv sync --locked`, `uv.lock` dosyasındaki sürümlerle `.venv` sanal ortamını hazırlar; geliştirme bağımlılığı olan `pytest` de kurulur. Kilit dosyası proje tanımıyla uyuşmuyorsa hata verir ve kilidi değiştirmez.

`.venv` Git'e dahil edilmez. Başka bir bilgisayarda aynı komutla yeniden oluşturulur. Komutları `uv run` ile çalıştırırken sanal ortamı elle etkinleştirmek gerekmez.

## Çalıştırma

    uv run yardim-masasi httpx fastapi
    uv run talep-ozeti
    uv run talep-ozeti ornek/talepler.json

`talep-ozeti`'ne dosya verilmezse `ornek/talepler.json` okunur.

## Talep Dosyası

Bir JSON listesi; her talep şu alanları taşır:

    id          sayı
    baslik      metin
    durum       acik, beklemede, kapali
    oncelik     yuksek, orta, dusuk
    etiketler   metin listesi (boş olabilir)
    musteri     e-posta adresi

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
    __init__.py       Komut satırı giriş noktası; paketleri sırayla sorgular.
    pypi.py           HTTP isteği, zaman aşımı ayarı ve çıktı biçimlendirmesi.
    metin.py          Türkçe harf dönüşümü, etiket temizleme ve metin yardımcıları.
    talepler.py       Talep filtreleme, sıralama, arama ve özet komutu.
tests/test_pypi.py     Özet biçimi ve ortam değişkeni testleri.
tests/test_metin.py    Türkçe metin yardımcılarının testleri.
tests/test_talepler.py Talep işlemlerinin testleri.
ornek/talepler.json    On iki örnek destek talebi.
notes/                Günlük öğrenme ve çalışma notları.
pyproject.toml        Proje tanımı, bağımlılıklar ve komutun giriş noktası.
uv.lock               Çözümlenmiş doğrudan ve dolaylı bağımlılıklar.
.python-version       Geliştirmede seçilen Python sürümü.
.env.example          Paylaşılabilir ortam değişkeni örneği.
```

Çalışma bağımlılıkları `httpx` ve `rich`, geliştirme bağımlılığı `pytest` olarak tanımlıdır. HTTP isteklerini `httpx` yapar. `rich` bağımlılıklarda bulunur, ancak mevcut çıktı düz `print` ile üretilir.

## Testler

```bash
uv run --locked pytest -q
```

Mevcut 31 testin beşi PyPI özetini ve zaman aşımı ayarını, 13'ü metin yardımcılarını, 13'ü talep işlemlerini kontrol eder. Testler gerçek PyPI isteği yapmaz; ağ hataları ve komut satırı akışı bu testlerin kapsamı dışındadır.

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

- Bulunamayan paket, bağlantı sorunu veya zaman aşımı için kullanıcıya özel hata mesajı yoktur; Python hata izi gösterilir. Bir sorgu hata verirse sonraki paketlere geçilmez.
- `PYPI_ZAMAN_ASIMI` sayıya çevrilemiyorsa `ValueError` oluşur. Değer aralığı için ayrıca doğrulama yapılmaz.
- Yardım ekranı, seçenek ayrıştırma, önbellek ve otomatik yeniden deneme bulunmaz.
- Bağımlılıklar için otomatik güvenlik açığı taraması yapılandırılmamıştır.
- `talep-ozeti`'ne verilen dosya yoksa ya da geçerli JSON değilse düzgün bir mesaj yok; Python'un hata izi basılır.
- Varsayılan `ornek/talepler.json` yolu komutun çalıştırıldığı klasöre göredir; proje kökünden başka bir klasörde dosya bulunamaz.
- Kapanmamış bir talepteki bilinmeyen bir `oncelik` değeri `talep-ozeti`'ni `KeyError` ile durdurur.

## Çalışma Notları ve Git Akışı

[23.10.2026 günlük özeti](notes/daily-summary-23-10-2026.md), Python ve uv ile ilgili öğrenme notlarını içerir.

[27.10.2026 günlük özeti](notes/daily-summary-27-10-2026.md), Python veri tipleri, metin işleme ve talep fonksiyonları üzerine öğrenme notlarını içerir.

Değişiklikler yerel çalışma alanında tutulur; kullanıcı açıkça istemeden commit veya GitHub'a push yapılmaz. Commit istendiğinde anlamlı işler ayrı commitlere ayrılır; push için ayrıca kullanıcının talebi gerekir.
