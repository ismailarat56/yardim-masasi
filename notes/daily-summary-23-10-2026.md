# 23.10.2026 Gün Sonu Özeti

Tamamlama notu (27.10.2026): Şablonun tarihi korunarak mevcut proje dosyaları ve yerel ortam üzerinden dolduruldu. `arrow` bölümü sürüm yönetimi örneğidir; paket şu an projenin bağımlılıklarında bulunmuyor.

## Python ve Yorumlayıcı

Python kodunu çalıştıran program yorumlayıcıdır. `python`, `python3` ve `uv run python` komutları, ortamın ayarlarına bağlı olarak farklı yorumlayıcılara ulaşabilir.

Bu projede `.python-version` dosyası `3.15`, `pyproject.toml` içindeki `requires-python` alanı `>=3.15` değerindedir. İlki geliştirmede seçilecek sürümü, ikincisi projenin desteklediğini bildirdiği Python aralığını belirler. Yerel sanal ortamda doğrulanan yorumlayıcı Python 3.15.1'dir.

```bash
uv run --locked python --version
uv run --locked python -c 'import sys; print(sys.executable)'
```

## Paketler Nereye Kurulur

`uv sync`, proje bağımlılıklarını proje dizinindeki `.venv` sanal ortamına kurar. Bu Linux ortamında paketler `.venv/lib/python3.15/site-packages`, çalıştırılabilir komutlar `.venv/bin` altında bulunur.

uv'nin indirme önbelleği ile sanal ortam farklı amaçlara hizmet eder: önbellek indirilen dosyaları tekrar kullanmayı sağlar; `.venv` bu projenin çalışacağı ortamdır. Proje kaynak kodu ise `src/yardim_masasi` altında kalır ve varsayılan geliştirme kurulumunda düzenlenebilir biçimde kullanılır.

## Sistem Python'u ve which

`which python3` veya kabuğun `command -v python3` komutu, `PATH` üzerinde bulunan ilk eşleşmeyi gösterir. Bu nedenle `python3` adı tek başına sistem Python'unun çalıştığını kanıtlamaz.

```bash
command -v python3
python3 --version
uv run --locked python -c 'import sys; print(sys.executable)'
```

Kontrol sırasında kabukta `python3`, projenin `.venv/bin/python3` dosyasına gidiyordu ve 3.15.1 sürümünü gösteriyordu; `/usr/bin/python3` ise 3.14.4 idi. Proje için farklı bir yorumlayıcı kullanmak sistem yorumlayıcısını değiştirmeyi gerektirmez.

## uv ile Python Sürümleri

```bash
uv python list --only-installed
uv python find 3.15
uv python install 3.15
uv python pin 3.15
```

`list` kurulu yorumlayıcıları gösterir, `find` uygun yorumlayıcının yolunu bulur, `install` seçilen sürümü kurar, `pin` ise proje seçimini `.python-version` dosyasına yazar. Python kurmak, o sürümü her projede otomatik olarak seçmek anlamına gelmez.

`uv run` proje ortamındaki komutu çalıştırır; bunun için önce `source .venv/bin/activate` yapmak gerekmez. Etkinleştirme, doğrudan `python` gibi komutları kullanırken kabuğun `PATH` sırasını değiştiren bir kolaylıktır.

## Sanal Ortamın İçi

| Konum | Görevi |
| --- | --- |
| `.venv/bin/python` | Ortamın Python yorumlayıcısına erişim sağlar; bu makinede uv'nin yönettiği Python'a sembolik bağdır. |
| `.venv/bin/yardim-masasi` | `pyproject.toml` içindeki giriş noktasından oluşturulan komuttur. |
| `.venv/bin/pytest` | Test çalıştırıcısıdır. |
| `.venv/lib/python3.15/site-packages` | Kurulu paketleri ve paket metadatasını içerir. |
| `.venv/pyvenv.cfg` | Sanal ortamın temel yorumlayıcı bilgilerini içerir. |

`sys.prefix` sanal ortamı, `sys.base_prefix` temel Python kurulumunu gösterir. Sanal ortam normalde sistem paketlerinden ayrıdır; bu, her projede farklı bağımlılık sürümleri kullanılmasını sağlar. `.venv` Git'e eklenmez ve proje dosyalarından yeniden kurulabilir.

## pyproject.toml ve uv.lock

`pyproject.toml` projenin tanımıdır: adı, Python koşulu, çalışma bağımlılıkları, geliştirme bağımlılıkları, derleme sistemi ve komut satırı giriş noktası burada yer alır. Mevcut çalışma bağımlılıkları `httpx>=0.28.1` ve `rich>=15.0.0`, geliştirme bağımlılığı `pytest>=9.1.1` olarak tanımlıdır.

`uv.lock`, bu koşullara göre seçilen kesin sürümleri, dolaylı bağımlılıkları, paket kaynaklarını ve dosya hashlerini kaydeder. İki dosya da Git'te tutulur; kilit dosyası uv tarafından üretilir.

- `uv add` ve `uv remove`, proje tanımını, kilidi ve sanal ortamı birlikte günceller.
- `uv lock`, kilit dosyasını günceller; kurulu ortamı tek başına eşitlemez.
- `uv sync --locked`, mevcut kilidi değiştirmeden ortamı eşitler; kilit güncel değilse hata verir.
- `uv run --locked`, kilidin değişmesini engelleyerek proje ortamında komut çalıştırır.

## Sürüm Aralıkları

| Koşul | Anlamı |
| --- | --- |
| `==1.3.0` | Yalnızca 1.3.0 sürümü. |
| `>=1.3.0` | 1.3.0 ve sonrası; üst sınır yoktur. |
| `>=1.3.0,<2.0.0` | En az 1.3.0, ancak 2.0.0'dan küçük sürümler. |
| `~=1.3.0` | En az 1.3.0, ancak 1.4.0'dan küçük sürümler. |

Bir aralık yeni sürüme izin verebilir, ancak kilitteki sürüm bu yüzden kendiliğinden değişmez. `uv lock --upgrade-package paket`, o paketin mevcut kilidini yeniden değerlendirir ve proje kısıtlarına uyan sürümü seçer. Sonrasında `uv sync --locked` kurulu ortamı günceller.

## Majör Yükseltme: arrow

Örnek olarak `arrow>=1.3.0,<2.0.0` koşulu varsa, `uv lock --upgrade-package arrow` komutu 2.x sürümüne geçemez. Bunun için önce proje koşulunun 2.x'e izin verecek şekilde değiştirilmesi gerekir. Buna karşılık yalnız `arrow>=1.3.0` yazıyorsa üst sınır yoktur; diğer koşullar da uygunsa 2.x'e geçiş mümkündür.

Majör sürüm yükseltmesi değerlendirilirken sürüm notları, desteklenen Python sürümleri ve kullanılan API'lerdeki değişiklikler kontrol edilir. Aralığı değiştirmek, kodun yeni sürümle uyumlu olduğunu tek başına kanıtlamaz; uygulamanın ilgili akışları ve testleri çalıştırılmalıdır.

Bu bölümde belirli bir `arrow` yükseltmesinin yapıldığı veya test edildiği kaydedilmiyor; mevcut `pyproject.toml` ve `uv.lock` içinde `arrow` yoktur.

## Python Sürümünü Yükseltmek

Projenin Python seçimi 3.14'ten 3.15'e, asgari Python koşulu da `>=3.14` değerinden `>=3.15` değerine yükseltildi. Kilit dosyasının Python koşulu da `>=3.15`.

Benzer bir geçişin adımları:

1. Bağımlılıkların hedef Python sürümünü desteklediğini kontrol et.
2. `uv python install 3.15` ile yorumlayıcıyı kur ve `uv python pin 3.15` ile proje için seç.
3. Desteklenen asgari sürüm de yükseltilecekse `pyproject.toml` içindeki `requires-python` alanını güncelle.
4. `uv lock` ve `uv sync --locked` ile kilidi ve ortamı eşitle.
5. `uv run --locked python --version` ve `uv run --locked pytest -q` ile sonucu doğrula.

Yalnız `.python-version` dosyasını değiştirmek, `requires-python` alanını otomatik olarak değiştirmez. Python sürümünü yükseltmek ile bir Python paketinin sürümünü yükseltmek de ayrı işlemlerdir.

## .env ve Ortam Değişkenleri

Kod, `PYPI_ZAMAN_ASIMI` değerini `os.getenv` ile okur ve `float` türüne çevirir. Değişken yoksa 10 saniye kullanılır; `2.5` gibi ondalık değerler kabul edilir. Sayıya çevrilemeyen değerler şu an `ValueError` üretir.

`.env.example`, paylaşılabilir örnek ayardır. Yerel `.env` dosyası `.gitignore` ile dışarıda tutulur. `.env` henüz yoksa:

```bash
cp .env.example .env
uv run --locked --env-file .env yardim-masasi httpx
```

Dosyayı oluşturmak tek başına değişkeni sürece aktarmaz; `--env-file` ile yüklemek gerekir. Alternatif olarak Bash'te tek komuta değer verilebilir:

```bash
PYPI_ZAMAN_ASIMI=2.5 uv run --locked yardim-masasi httpx
```

## Yanıldığım İki Tahmin

Bu başlık için iki teknik düzeltme notu:

1. **“`python3` her zaman sistem Python'udur.”** Komutun hangi dosyaya gideceğini `PATH` belirler. Sanal ortam etkinken veya yolu öne alınmışken proje yorumlayıcısı çalışabilir; `sys.executable` ile doğrulanır.
2. **“Paketin daha yeni sürümü varsa `uv sync` mutlaka onu kurar.”** Proje tanımıyla uyumlu kilit dosyası mevcut sürümü korur. Bilinçli yükseltme için ilgili paket yeniden çözümlenir; izin verilen aralık yine geçerlidir.

## En Çok Zorlandığım Konu

Tekrar notu: yorumlayıcı seçimi, kurulu paketler ve sürüm kurallarını ayrı takip etmek. Kontrol sırası şu şekilde tutulabilir:

1. **Hangi Python çalışıyor?** `uv run --locked python -c 'import sys; print(sys.executable)'`
2. **Hangi sürümlere izin veriliyor?** `.python-version` ve `pyproject.toml`.
3. **Hangi paket sürümleri seçilmiş?** `uv.lock` ve `uv tree --locked`.
4. **Bu seçimler ortama uygulanmış mı?** `uv sync --locked` ve testler.

27.10.2026 doğrulamasında `uv run --locked pytest -q` ile mevcut 5 test geçti. Bu testler çıktı biçimini ve zaman aşımı ayarını kapsıyor; gerçek ağ hataları için otomatik test bulunmuyor.

Ayrıca `uv run --locked --env-file .env.example yardim-masasi httpx fastapi` komutu gerçek PyPI verisiyle çalıştırıldı; iki paket için de sürüm ve Python koşulu başarıyla yazdırıldı.
