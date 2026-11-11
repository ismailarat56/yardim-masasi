# 10.11.2026 Gün Sonu Özeti

## Alembic Kurulumu

`uv add alembic` ile Alembic'i ekleyip `alembic init migrations` ile `alembic.ini` dosyasını ve `migrations/` klasörünü oluşturdum. Veritabanı adresini `alembic.ini`'ye yazmadım; `migrations/env.py` adresi `DATABASE_URL`'den, yani API'nin kullandığı `baglanti_adresi()` fonksiyonundan alıyor. Böylece parola Git'e girmiyor ve API ile Alembic aynı veritabanına bakıyor.

## İlk Revizyon ve stamp

İlk revizyonu `--rev-id 0001` ile açtım ve `sql/001_talepler.sql` içindeki `CREATE TABLE`'ı `op.execute` ile içine taşıdım; `downgrade` tabloyu siliyor. Asıl veritabanında tablo zaten vardı, bu yüzden `upgrade head` 0001'i yeniden çalıştırıp "relation already exists" hatası verirdi. `alembic stamp 0001` şemaya dokunmadan yalnızca `alembic_version` tablosuna "bu veritabanı 0001'de" diye yazıyor; sonraki revizyonlar oradan devam ediyor.

## Testlerde Şema

Testler artık tabloyu SQL dosyasından değil, migration'lardan kuruyor. `conftest.py`'deki oturum kapsamlı `test_adresi` fikstürü test veritabanının `public` şemasını bir kez silip `command.upgrade(..., "head")` çalıştırıyor; her test ise yalnızca `TRUNCATE ... CASCADE` ile tabloları boşaltıyor. Fikstür `alembic.ini`'yi okumadan kendi `Config` nesnesini kurduğu için testler yanlışlıkla `DATABASE_URL`'e migration uygulayamıyor. `test_gocler.py` her revizyonun geri alınıp yeniden uygulanabildiğini denetliyor.

## surum Sütunu ve server_default

0002 revizyonu `talepler` tablosuna `surum` sütununu ekledi. Sütun `NOT NULL` olduğu için dolu bir tabloya varsayılan değer olmadan eklenemezdi; `server_default="1"` var olan satırları da 1 ile dolduruyor ve yeni satırlar için veritabanında varsayılan olarak kalıyor. Python tarafındaki bir varsayılan ise yalnızca Python'dan eklenen satırlara etki ederdi, eski satırlara değil.

## Kayıp Güncelleme

İki kişi aynı talebi okuyup ikisi de değiştirdiğinde ikinci yazan, birincinin değişikliğini haberi olmadan eziyor; buna kayıp güncelleme deniyor. Her iki istek de kendi açısından başarılı göründüğü için hata mesajı bile çıkmıyor. Çözüm, yazarken "ben bu talebi şu sürümde görmüştüm" bilgisini de göndermek ve sürüm değiştiyse yazmayı reddetmek.

## Sürüm Kontrollü guncelle

`guncelle` artık `surum` parametresi istiyor ve kontrol ile yazmayı tek komutta yapıyor: `UPDATE ... SET surum = surum + 1 WHERE id = ... AND surum = ...`. Önce `SELECT` ile sürüme bakıp sonra `UPDATE` yapsaydım iki istek arasındaki boşlukta yine çakışma olabilirdi. `UPDATE` satır döndürmezse ikinci bir `SELECT` ile talebin hiç olmadığını (`None`) ya da sürümün tutmadığını (`SurumCakismasi`) ayırıyorum; aynı anda gönderilen iki güncellemeden yalnız birinin yazıldığını `asyncio.gather` ile yirmi turda denedim.

## ETag, If-Match, 412 ve 428

`GET /talepler/{id}` sürümü `ETag: "3"` gibi tırnaklı bir başlıkla veriyor; istemci bunu `PATCH`'te `If-Match` başlığıyla geri gönderiyor. Sürüm eskiyse `412 Precondition Failed` dönüyor ve yanıtın `ETag`'i güncel sürümü gösteriyor; başlık hiç yoksa `428 Precondition Required`, biçimsizse `400`. `428` sayesinde istemci koşulsuz yazıp başkasının değişikliğini ezemiyor.

## Yorumlar ve Yabancı Anahtar

0003 revizyonu `yorumlar` tablosunu ekledi; `talep_id`, `talepler.id`'ye `ON DELETE CASCADE` ile bağlı. Yabancı anahtar, olmayan bir talebe yorum eklenmesini veritabanı düzeyinde engelliyor; depo bu durumda `ForeignKeyViolation` yakalayıp `None` dönüyor. Yan etkisi, `TRUNCATE talepler`'in artık `CASCADE` olmadan çalışmaması oldu.

## Yorum Uçları ve Testlerim

`GET` ve `POST /talepler/{id}/yorumlar` uçlarını ekledim; ekleme API anahtarı istiyor, gövdede yalnızca `yazan` ve `metin` var. Testlerde olmayan talebe `404`, boşluktan ibaret metne ve gövdede `talep_id` gönderilmesine `422`, anahtarsız isteğe `401` dönüldüğünü ve yorumun talebin `ETag`'ini değiştirmediğini denetledim. Her ek testi, üretim kodunu geçici olarak bozup önce kırmızı gördüm.

## Araştırma Notları

> **Doldurulacak:** 12. ve 13. görevlerin soruları bu oturumda elimde değil; sorular gelince kendi cümlelerimle cevaplanacak.

## Live Board'dan Farklı Üç Şey

Birincisi, Live Board'daki `migrate.ts` SQL dosyalarını sırayla çalıştıran kendi yazdığımız bir betikti; Alembic ise revizyonları `down_revision` ile bir zincire bağlıyor, geri alma (`downgrade`), `stamp` ve `--sql` ile çevrimdışı çıktı gibi işleri hazır veriyor. İkincisi, orada beklenen sürüm gövdedeki `expectedVersion` alanıyla gidiyordu; burada HTTP'nin kendi koşullu istek mekanizması olan `If-Match` başlığını kullanıyorum, böylece gövde yalnızca değişikliği taşıyor. Üçüncüsü, orada çakışma `409 Conflict` ile bildiriliyordu; burada önkoşul başlıkta verildiği için doğru kod `412 Precondition Failed`, başlığın hiç olmaması ise `428`.

## Yanıldığım İki Tahmin

> **Doldurulacak:** Bugün "önce tahmin et" denen yerlerdeki gerçek tahminlerim buraya yazılacak.

## En Çok Zorlandığım Konu

En çok zorlandığım konu, sürüm kontrolünün neden tek bir `UPDATE` içinde yapılması gerektiğini kavramak oldu. Önce okuyup sonra yazan bir kod tek istekte doğru çalışıyor, hata ancak iki istek aynı anda geldiğinde çıkıyor; bunu bellek deposunda görmek mümkün değildi. Eşzamanlı testi yalnızca PostgreSQL'de koşturup yirmi turda her seferinde tek yazma görünce ne korumaya çalıştığımı daha iyi anladım.
