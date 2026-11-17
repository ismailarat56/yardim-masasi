# 15.11.2026 Gün Sonu Özeti

## İlk Dockerfile

İlk Dockerfile bilerek saftı: `python:3.15-slim` üstüne uv'yi kopyalayıp `COPY . .` ile bütün klasörü aldı, `uv sync --locked` ile kurdu. Derleme bağlamı 142 MB çıktı, çoğu `.venv`'di; uv kopyalanan `.venv`'i makinenin Python'una bağlı olduğu için silip yeniden kurdu, dev paketleriyle 72 paket indi. Daha kötüsü `.env`, `.env.db` ve `.git` imaja girdi: API anahtarı imajdan `cat .env` ile okunabiliyordu. `.gitignore` Git'i korur, Docker'ı korumaz.

## .dockerignore

`.dockerignore`, derleme bağlamından çıkarılacakları yazar; o dosyalar derleyiciye hiç gönderilmez. `.gitignore`'a benziyor ama kuralları aynı değil: `__pycache__/` yalnız kökteki klasöre uyduğu için `src/yardim_masasi/__pycache__` ve `.pytest_cache` imaja girdi. Her klasördekini dışlamak için `**/__pycache__` yazmak gerekti.

## Katmanlar ve uv

Her `COPY` ve `RUN` ayrı bir katman; bir adımın önbelleği, girdileri ve önceki bütün adımlar aynı kaldıysa kullanılıyor. `COPY . .` en başta olunca tek satırlık kod değişikliği 72 paketi baştan indirtti. Önce yalnız `pyproject.toml` ve `uv.lock`'u kopyalayıp `--no-install-project --no-dev` ile bağımlılıkları kurunca kod değişikliğinde bağımlılık adımı `CACHED` geldi ve derleme 22 saniyeden 1.7 saniyeye indi. `CMD`'de `uv run` kullanınca uv her açılışta ortamı varsayılan gruplarla eşitlediği için imajda olmayan pyright'ı indirdi; bu yüzden `ENV PATH` ile `.venv/bin`'i öne alıp komutu doğrudan çalıştırıyoruz.

## Kabın Ağı

Her kabın kendi ağ ortamı var: kabın içinde `127.0.0.1` kabın kendisi, bu yüzden `.env`'deki `127.0.0.1:5434` ile uygulama açılamadı ve 3 koduyla çıktı. Compose'un ağına girince `db` adı çözüldü ama `db:5434` de olmadı; `5434` yalnız makinenin kapısı, ağın içinden PostgreSQL'in kendi portu `5432` kullanılıyor. `fastapi dev` yalnız `127.0.0.1`'i dinlediği için kabın içinden ulaşılabildi, makineden ulaşılamadı; kapta `0.0.0.0`'ı dinleyen `fastapi run` gerekiyor.

## Compose ve Migration

Uzun `docker run` satırı `compose.yaml`'da `api` servisi oldu; `environment` altındaki `DATABASE_URL`, `env_file: .env`'dekini eziyor. Boş bir veritabanında `/saglik` `ok` dedi ama `/talepler` `UndefinedTable` ile 500 döndü: `SELECT 1` tablo istemiyor. Migration'ı uygulamanın açılışına koymak yerine ayrı, tek seferlik bir `migrate` servisi yazdık; API'nin birden çok kopyası olsa her biri aynı migration'ı denerdi. Sıra `db` sağlıklı → `migrate` 0 koduyla bitti → `api` başladı.

## Düzgün Kapanış

Exec biçimindeki `CMD ["fastapi", "run", ...]`'de uygulama kabın 1 numaralı süreci; `docker compose stop`'un gönderdiği `SIGTERM`'i doğrudan alıp bir saniyeden kısa sürede kapanıyor. Shell biçiminde 1 numaralı süreç `sh` oluyor ve sinyali uygulamaya iletmiyor; Docker 10 saniye bekleyip `SIGKILL` gönderiyor, kap `137` (128 + 9) koduyla çıkıyor.

## Sağlık Ucu

Veritabanı durunca ilk `/saglik` isteği havuzdaki kopuk bağlantıyı alıp hemen hata verdi (`AdminShutdown`); sonrakiler `db` adı çözülemediği için havuzun 30 saniyelik bekleme süresi dolana kadar asılı kaldı. `havuz.connection(timeout=2)` bu bekleyişi yalnız `/saglik` için 2 saniyeye indirdi. `except OperationalError` hem `PoolTimeout`'u hem kopuk bağlantının hatasını yakalıyor ve `503` döndürüyor; başka hatalar yutulmuyor, çünkü onlar "veritabanı yok" değil, kodda bir hata demek.

## Sağlık Testlerim

Testlerde lifespan çalışmadığı için havuz yok; `SahteHavuz`'u `monkeypatch` ile `app.state.havuz`'a koydum. Beş test yazdım: veritabanı cevap verince 200 ve `SELECT 1`, havuz bekletince 503, bağlantı kopunca 503, havuzdan istenen sürenin `[2]` olması ve `RuntimeError`'ın yutulmaması. Yalnız `PoolTimeout`'u yakalayan bozma kopuk bağlantı testini, `timeout`'u unutan bozma 2 saniye testini kırdı; ikisini de testlerim yakaladı.

## Kabın Sağlık Kontrolü

`api`'ye kabın içinden `/saglik`'e istek atan bir `healthcheck` ekledik: 5 saniyede bir, 3 saniyelik zaman aşımıyla, üç başarısızlıkta `unhealthy`. Zaman aşımının `/saglik`'in 2 saniyelik bekleyişinden uzun olması gerekiyor, yoksa veritabanı sağlamken bile kontrol düşer. Veritabanı durunca kap `unhealthy 5` oldu ama yeniden başlatılmadı, yalnız işaretlendi; veritabanı açılınca bir saniyede `healthy`'ye döndü. `docker compose up -d --wait` artık "birkaç saniye bekle" demeyi gereksiz kılıyor.

## İki Aşamalı İmaj

Kap root olarak çalışıyordu ve uv imajda kalmıştı. `kur` aşaması bağımlılıkları kuruyor, `calis` aşaması yalnız `/app`'i alıyor ve `uygulama` kullanıcısıyla çalışıyor; dosyalar root'a ait olduğu için uygulama kodunu değiştiremiyor. Yalnız `.venv`'i kopyalayınca uygulama içe aktarılamıyor, çünkü proje `.venv`'e kodun yerini gösteren bir bağlantıyla kuruluyor ve kod `/app/src`'de kalıyor; iki aşamanın tabanı da aynı olmalı, çünkü `.venv/bin/python` taban imajdaki Python'a bir bağlantı. `kap_denetle.py` tek aşamalı imajda 9/12, iki aşamalıda 12/12 verdi; imaj 412 MB'tan 313 MB'a indi.

## Temiz Klon

Bugün kurduğum her şeyin Git'te olup olmadığını görmek için projeyi `/tmp/ym-temiz`'e klonlayıp yalnız iki `.env` dosyasını örneklerinden kopyalamak ve `docker compose -p ym-temiz up -d --build --wait` ile yığını kaldırmak gerekiyor. Klon yalnız commit edilmiş dosyaları getirdiği için commit'lenmeden unutulan bir dosya burada ortaya çıkar. Ben değişikliklerimi henüz commit'lemediğim için bu adımı uygulamadım, yalnız inceledim; commit'lerden sonra denenmeli.

## Araştırma Notları

> **Doldurulacak:** 13. ve 14. görevlerin soruları bu oturumda elimde değil; sorular gelince kendi cümlelerimle cevaplanacak.

## Yanıldığım İki Tahmin

> **Doldurulacak:** Bugün "tahmin et" denen yerler: imaja hangi dosyaların gireceği, `.env`'in girip girmeyeceği ve `.venv`'e ne olacağı; uygulamanın `.env`'deki adresle açılıp açılmayacağı; `db:5434`'ün çalışıp çalışmayacağı. Gerçek tahminlerim buraya yazılacak.

## En Çok Zorlandığım Konu

En çok zorlandığım konu kabın ağıydı: aynı `127.0.0.1` adresinin makinede veritabanını, kabın içinde ise kabın kendisini göstermesi. `-p 127.0.0.1:5434:5432`'nin solunun makineye, sağının kaba ait olduğunu ve ağın içinden doğrudan `db:5432`'ye gidildiğini, iki yanlış adresin verdiği iki farklı hatayı (`127.0.0.1`'de bağlantı reddi, `db:5434`'te çözülen adrese rağmen bağlantı reddi) yan yana görünce anladım.
