[← README'ye dön](../README.md)

# Geliştirme

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

## Çalışma Notları ve Git Akışı

[23.10.2026 günlük özeti](../notes/daily-summary-23-10-2026.md), Python ve uv ile ilgili öğrenme notlarını içerir.

[27.10.2026 günlük özeti](../notes/daily-summary-27-10-2026.md), Python veri tipleri, metin işleme ve talep fonksiyonları üzerine öğrenme notlarını içerir.

[28.10.2026 günlük özeti](../notes/daily-summary-28-10-2026.md), sınıflar, talep modeli, sınırda doğrulama ve çıkış kodları üzerine öğrenme notlarını içerir.

[06.11.2026 günlük özeti](../notes/daily-summary-06-11-2026.md), parametre türleri,
zamanlı talepler, filtreler, argparse, logging ve testlerle ilgili çalışma
notlarını içerir.

[07.11.2026 günlük özeti](../notes/daily-summary-07-11-2026.md), tip denetimi,
generic dekoratörler, asyncio, iptal ve eşzamanlı PyPI sorgularını açıklar.

[09.11.2026 günlük özeti](../notes/daily-summary-09-11-2026.md), PostgreSQL kabı,
psycopg, bağlantı havuzu, Pydantic şemaları, FastAPI uçları ve API testlerini anlatır.

[10.11.2026 günlük özeti](../notes/daily-summary-10-11-2026.md), Alembic migration'ları,
sürüm kontrollü güncelleme, ETag/If-Match ve yorumları anlatır.

Değişiklikler yerel çalışma alanında tutulur; kullanıcı açıkça istemeden commit veya GitHub'a push yapılmaz. Commit istendiğinde anlamlı işler ayrı commitlere ayrılır; push için ayrıca kullanıcının talebi gerekir.
