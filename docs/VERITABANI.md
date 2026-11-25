[← README'ye dön](../README.md)

# Veritabanı

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

Alembic bağlanacağı adresi `alembic.ini`'den değil, `DATABASE_URL`'den alır. Test veritabanına elle `upgrade` gerekmez; testler şemayı kendileri kurar (bkz. [Testler](GELISTIRME.md#testler)).

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
