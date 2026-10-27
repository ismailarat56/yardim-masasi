# Yardım Masası

`yardim-masasi`, verilen Python paketlerinin PyPI'da bildirilen güncel sürümünü ve desteklediği Python sürüm aralığını terminalde gösteren küçük bir komut satırı aracıdır. Paketleri kurmadan bilgilerini sorgular.

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

Tek paket veya boşlukla ayrılmış birden fazla paket sorgulanabilir:

```bash
uv run --locked yardim-masasi httpx
uv run --locked yardim-masasi httpx fastapi
```

Örnek çıktı biçimi; gerçek sürümler PyPI yanıtına göre değişir:

```text
httpx 0.28.1 (Python >=3.8)
```

Paketin Python sürüm koşulu boşsa `Python belirtilmemiş` yazılır. Paket adı verilmezse program çıktı üretmeden sonlanır.

Komut, her paket için `https://pypi.org/pypi/{paket}/json` adresine sırayla istek yapar. Yanıtın `info.name`, `info.version` ve `info.requires_python` alanlarını kullanır; kurulu paketleri veya projedeki sürüm kısıtlarını denetlemez.

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
tests/test_pypi.py     Özet biçimi ve ortam değişkeni testleri.
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

Mevcut beş test; paket adı/sürüm/Python bilgisinin biçimlendirilmesini, Python koşulunun `None` veya boş metin olmasını ve zaman aşımının varsayılan ya da ortam değişkeninden alınmasını kontrol eder. Testler gerçek PyPI isteği yapmaz; ağ hataları ve komut satırı akışı bu testlerin kapsamı dışındadır.

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

## Çalışma Notları ve Git Akışı

[23.10.2026 günlük özeti](notes/daily-summary-23-10-2026.md), Python ve uv ile ilgili öğrenme notlarını içerir.

Değişiklikler yerel çalışma alanında tutulur; kullanıcı açıkça istemeden commit veya GitHub'a push yapılmaz. Commit istendiğinde anlamlı işler ayrı commitlere ayrılır; push için ayrıca kullanıcının talebi gerekir.
