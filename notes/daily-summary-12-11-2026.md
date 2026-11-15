# 12.11.2026 Gün Sonu Özeti

## On Bin Talep ve OFFSET

Tabloyu on bin taleple doldurunca `GET /talepler` bütün talepleri tek yanıtta döndürdüğü için yanıt kocamanlaştı; sayfalamak gerekti. İlk akla gelen `LIMIT ... OFFSET ...` iki soruna takılıyor: PostgreSQL atlanan satırları da baştan okuyup attığı için sayfa ilerledikçe sorgu yavaşlıyor, ve iki sayfa arasında yeni bir talep eklenince bütün satırlar bir kayıyor, bir talep iki kez görünüyor ya da hiç görünmüyor.

## Ayraçlı Sayfalama

Ayraçlı sayfalamada sonraki sayfa "kaçıncı satırdan" değil, "önceki sayfanın son talebinden sonra" diye tarif ediliyor. Sıra `ORDER BY acildi DESC, id DESC`, koşul `(acildi, id) < (son_acildi, son_id)`; satır karşılaştırması aynı anda açılmış talepleri `id` ile ayırıyor. Böylece her sayfa aynı hızda geliyor ve araya giren talep sayfaları kaydırmıyor.

## (acildi, id) Indexi

0004 revizyonu `talepler` üzerine `(acildi, id)` indeksini ekledi. Sıralama ve ayraç koşulu tam bu iki sütunu kullandığı için PostgreSQL indeksi tersten okuyup ilk `limit + 1` satırda durabiliyor, bütün tabloyu sıralamıyor. `downgrade` yalnızca indeksi siliyor.

## Ayraç ve Opak Metin

`sayfa.py` içindeki `Ayrac`, bir sayfanın son talebinin `(acildi, id)` çiftini tutuyor. `ayrac_yaz` bunu kısa bir JSON'a, sonra adreste kaçışsız kullanılabilen URL güvenli base64'e çeviriyor; `ayrac_oku` tersini yapıyor ve bozuk, saat dilimsiz ya da numarası pozitif tam sayı olmayan her metni `GecersizAyrac` ile reddediyor. Ayraç istemciye opak bir metin olarak veriliyor; istemcinin içine bakmaması, olduğu gibi geri yollaması bekleniyor, böylece biçimi ileride istemcileri bozmadan değişebilir.

## Sayfalı listele

İki deponun `listele`'si artık liste değil `Sayfa(talepler, sonraki)` döndürüyor ve `sonra` ile `limit` alıyor. Sorgu `limit + 1` satır istiyor: fazladan satır geldiyse sonraki sayfa var demek, `sonraki` gösterilen son talepten kuruluyor; gelmediyse `None`. Böylece sonraki sayfanın olup olmadığını öğrenmek için ayrıca `COUNT` sorgusu gerekmiyor ve tam dolan son sayfada boş bir sayfaya işaret eden ayraç verilmiyor.

## Liste Ucu

`GET /talepler` artık `{"talepler": [...], "sonraki": "..."}` biçiminde tek bir sayfa döndürüyor. `limit` varsayılan 20, 1–100 aralığında; dışındaki değer `422` alıyor. `?ayrac=` ile gelen metin bir bağımlılıkta okunuyor; okunamazsa `400` dönüyor, çünkü bu bir şema hatası değil, istemcinin bizim verdiğimiz metni bozması.

## Tam Metin Arama

`LIKE '%fatura%'` hem indeks kullanamıyor hem de Türkçe eklerle baş edemiyor: "faturam" ya da "Faturası" yazınca ya bulamıyor ya da yanlış yerden eşleşiyor. PostgreSQL'in tam metin araması metni `to_tsvector('turkish', ...)` ile köklerine indirilmiş kelimelere, aramayı `websearch_to_tsquery` ile bir sorguya çeviriyor ve `@@` ile eşleştiriyor. `websearch_to_tsquery` kullanıcı yazısını hata vermeden okuyor; boşluk "ve", `or` "veya", `-kelime` "olmasın", tırnak "bu sırayla" anlamına geliyor.

## arama Sütunu ve GIN

0005 revizyonu `talepler`'e `to_tsvector('turkish', baslik)` ile hesaplanan, `STORED` bir `arama` sütunu ve üzerine GIN indeksi ekledi. Sütun başlıktan veritabanı tarafından hesaplandığı için ekleme ve güncelleme kodunda hiçbir şey değişmedi; yeni talep hemen aranabilir oluyor. PostgreSQL 18'de `sa.Computed(...)` içinden `persisted=True` silinirse sütun `VIRTUAL` olarak kuruluyor ve indeks adımı `ERROR: indexes on virtual generated columns are not supported` hatasıyla duruyor; GIN indeksi için değerin diskte saklanması gerekiyor.

## Arama Ucu

`GET /talepler?ara=...` arama koşulunu depoya veriyor; `ara` 2–100 karakter, dışındaki değer `422` alıyor. Sonuçlar alakaya göre değil, listeyle aynı sırada geliyor ve aynı ayraçla sayfalanıyor; alaka sırası ayracı `(acildi, id)` ile tutarsız kılardı. Bellek deposundaki arama yalnızca kelimelerin geçip geçmediğine bakan kaba bir taklit, bu yüzden arama sözleşmesini yalnızca PostgreSQL'de test ettim.

## Koşullu GET ve 304

`GET /talepler/{id}` artık `If-None-Match` başlığını okuyor; elindeki `ETag` güncelse istemci gövdesiz `304 Not Modified` alıyor. Karşılaştırma zayıf: `W/"3"` ile `"3"` aynı sayılıyor, virgülle ayrılmış etiketlerden biri tutması yetiyor, `*` her etikete uyuyor. Talep yoksa önce `404` dönüyor; olmayan bir şey için "değişmedi" demek yanlış olurdu.

## Liste Ucu Testlerim

`limit=2` ile iki talep ve bir `sonraki` geldiğini, ayracı izleyince son sayfada `sonraki`'nin `null` olduğunu, `0`, `101` ve `abc` değerlerinin `422`, `100`'ün kabul edildiğini denetledim. Yirmiden fazla talep ekleyip varsayılan sayfanın yirmi talep ve bir ayraç verdiğini, ayracın `durum` süzgeciyle birlikte çalıştığını ve `ara` ile `durum`'un birlikte uygulandığını da test ettim.

## Araştırma Notları

> **Doldurulacak:** 12. ve 13. görevlerin soruları bu oturumda elimde değil; sorular gelince kendi cümlelerimle cevaplanacak.

## Yanıldığım İki Tahmin

> **Doldurulacak:** Bugün "önce tahmin et" denen yerlerdeki gerçek tahminlerim buraya yazılacak.

## En Çok Zorlandığım Konu

En çok zorlandığım konu, ayracın neden tek başına `id` değil `(acildi, id)` çifti olması gerektiğiydi. Sıra açılış zamanına göre olduğu için yalnız `id` ile "bundan küçük" demek sırayı bozuyor; yalnız `acildi` ile demek ise aynı anda açılmış talepleri ya iki kez veriyor ya atlıyor. Zamanları karışık ve bazıları eşit olan altı talepte her `limit` değeriyle bütün sayfaları okuyup her talebin bir kez geldiğini görünce çiftin neden gerektiğini anladım.
