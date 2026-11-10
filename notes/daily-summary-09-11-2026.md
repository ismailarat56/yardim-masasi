# 09.11.2026 Gün Sonu Özeti

## PostgreSQL Kabı ve Tablo

PostgreSQL'i bilgisayara kurmak yerine `compose.yaml` ile bir Docker kabında çalıştırdım. Portu yalnızca `127.0.0.1:5434` adresine açtım, verileri de kap silinse bile kalsın diye `db-data` biriminde tuttum. Sağlık denetimi, kabın çalışıyor olmasıyla veritabanının bağlantı kabul etmeye hazır olması arasındaki farkı gösteriyor. `sql/001_talepler.sql` ise kuralları veritabanına da yazıyor: Python kodunda hata olsa bile boş başlık ya da tanımsız durum tabloya giremiyor.

## psycopg: Parametre, Demet ve İşlem

Değerleri SQL metnine yapıştırmak yerine `%s` yer tutucularıyla ayrı gönderiyorum. Tek değer verirken bile demet gerekiyor; `(talep_id,)` yazımındaki virgül unutulursa parantez yalnızca gruplama oluyor. `with psycopg.connect(...)` bloğu hatasız biterse commit, hata çıkarsa rollback yapıyor; bu yüzden bir işlemdeki eklemeler ya hep birlikte kaydediliyor ya da hiçbiri kaydedilmiyor.

## Örnek Veriler ve Numara Sayacı

`talep-yukle` dosyadaki talepleri numaralarıyla birlikte ekliyor ve tablo doluysa hiçbir şey eklemeden `1` koduyla çıkıyor. Numaraları elle verdiğimde `id` sütununun sayacı bundan haberdar olmuyor ve 1'de kalıyor; ilk API eklemesi var olan bir numarayla çakışıyordu. `setval` ile sayacı en büyük numaraya ayarlamak bu sorunu çözdü; sözleşme testindeki "yeni numara 6 olur" denetimi de bunu koruyor.

## SQL Enjeksiyonu ve LiteralString

Kullanıcıdan gelen bir metin SQL'in parçası yapılırsa `hesap' OR '1'='1` gibi bir değer sorgunun anlamını değiştirebiliyor. Yer tutucu kullandığımda bu metin yalnızca veri olarak gidiyor; testte böyle bir etiket hiçbir talep döndürmüyor. psycopg'nin `LiteralString` beklemesi, dışarıdan gelen bir metnin sorgu olarak verilmesini tip denetimi aşamasında yakalıyor. Kendi SQL dosyamı okurken bunu `cast` ile bilerek aştım, çünkü o metin kullanıcıdan gelmiyor.

## Bağlantı Havuzu ve Lifespan

Her istekte yeni bağlantı açmak yavaş olduğu için `AsyncConnectionPool` birkaç bağlantıyı açık tutuyor ve istekler bunları ödünç alıp geri veriyor. Havuzu FastAPI'nin lifespan fonksiyonunda açıp `app.state`'e koyuyorum; `yield`'den sonrası uygulama kapanırken havuzu kapatıyor. `open(wait=True, timeout=5)` sayesinde veritabanına ulaşılamıyorsa uygulama ilk istekte değil, başlarken hata veriyor.

## Şemalar

`sema.py`'deki Pydantic modelleri API'nin dış dünyayla sözleşmesi; `Talep` modeli ise programın içindeki veri olarak kalıyor. `StringConstraints` boşlukları uzunluk denetiminden önce temizliyor, `extra="forbid"` ise istemcinin `durum` ya da `id` gibi kendisinin seçmemesi gereken alanları göndermesini `422` ile engelliyor. `TalepGuncelle`'deki model doğrulayıcı, iki alanın da boş olduğu güncellemeyi reddediyor.

## PgTalepDeposu

Depo, SQL'i tek bir sınıfta topluyor; uçlar yalnızca `getir`, `ekle`, `listele`, `guncelle` ve `durum_sayilari` metotlarını çağırıyor. İsteğe bağlı filtreleri `(%(durum)s::text IS NULL OR durum = %(durum)s)` kalıbıyla tek sorguda yazdım; kısmi güncellemede de `coalesce` verilmeyen alanın eski değerini koruyor. `RETURNING` eklenen ya da güncellenen satırı ayrıca `SELECT` yapmadan geri veriyor.

## Uçlar ve API Anahtarı

Altı uçtan dördü okuma yapıyor ve açık; `POST` ile `PATCH`, `X-API-Anahtari` başlığını sunucudaki `API_ANAHTARI` değeriyle karşılaştırıyor. Anahtar tanımlı değilse yazma tamamen kapalı oluyor; ayarı unutmak API'yi herkese açmıyor. Karşılaştırmayı `secrets.compare_digest` ile bayt olarak yapıyorum: bu hem zamanlama farkından bilgi sızmasını önlüyor hem de ASCII olmayan bir başlığın `500` yerine `401` almasını sağlıyor.

## API Testleri ve dependency_overrides

API testlerinde `app.dependency_overrides[depo_al]` ile gerçek depo yerine `BellekDeposu` veriliyor; `TestClient` `with` içinde kullanılmadığı için lifespan çalışmıyor ve havuz hiç açılmıyor. Sahte deponun gerçeğiyle aynı davrandığına güvenmek için sözleşme testleri aynı denetimleri iki depoda da koşturuyor. Geçersiz kılmaları her testten sonra temizlemek, modül düzeyindeki `app` nesnesi üzerinden diğer testlere sızmalarını önlüyor.

## Uç Sırası

FastAPI rotaları tanımlandıkları sırayla deniyor. `/talepler/ozet`, `/talepler/{talep_id}`'den sonra tanımlansaydı `ozet` kelimesi talep numarası olarak okunmaya çalışılır ve sayı olmadığı için `422` dönerdi. Bu yüzden sabit yolu değişkenli yoldan önce tanımladım; `test_ozet` bu sırayı koruyor.

## Araştırma Notları

> **Doldurulacak:** 12. ve 13. görevlerin soruları bu oturumda elimde değil; sorular gelince kendi cümlelerimle cevaplanacak.

Gün sonu kontrolünde `uv run --locked --env-file .env pytest -q` sonucu 264 başarılı test oldu. `--env-file` olmadan aynı komut 244 başarılı ve 20 atlanan test verdi; atlananlar `TEST_DATABASE_URL` tanımlı olmadığı için çalışmayan `[pg]` sözleşme testleri.

## TypeScript'ten Farklı Üç Şey

Birinci fark, FastAPI'nin fonksiyon parametrelerinin tip açıklamalarını çalışma anında okuyup gelen veriyi doğrulaması; TypeScript'te tipler derlemede silindiği için Express gibi bir çatıda aynı doğrulamayı Zod gibi ayrı bir kütüphaneyle yazmam gerekiyor. İkinci fark, bağımlılıkların `Depends(depo_al)` ile parametre tipine iliştirilmesi; TypeScript tarafında bu iş genellikle ara katman (middleware) ya da elle kurulan bir bağımlılık konteyneriyle yapılıyor. Üçüncü fark, psycopg'nin PostgreSQL dizilerini Python listesine, `timestamptz` değerlerini saat dilimli `datetime` nesnesine kendisi çevirmesi; Node'daki `pg` sürücüsünde zaman değerleri saat dilimi bilgisi taşımayan `Date` nesneleri olarak geliyor.

## Yanıldığım İki Tahmin

> **Doldurulacak:** Bugün "önce tahmin et" denen yerlerdeki gerçek tahminlerim buraya yazılacak.

## En Çok Zorlandığım Konu

En çok zorlandığım konu, bağlantının, işlemin ve havuzun ömrünü birbirinden ayırmak oldu. Havuzdan alınan bağlantının blok sonunda commit edilip havuza geri döndüğünü, havuzun ise uygulama ömrü boyunca açık kaldığını ayrı ayrı düşünmem gerekti. Testlerde bir yandan senkron bağlantıyla tabloyu kurup bir yandan async havuzla depoyu kullanmak bu ayrımı netleştirdi.
