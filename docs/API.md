[← README'ye dön](../README.md)

# API

```bash
uv run --env-file .env fastapi dev src/yardim_masasi/api.py
```

Sunucu `http://127.0.0.1:8000` adresinde açılır ve kod değiştikçe kendini yeniden başlatır. Başlarken bağlantı havuzunu açar; `DATABASE_URL` tanımlı değilse ya da veritabanına beş saniye içinde bağlanılamazsa başlamaz. `http://127.0.0.1:8000/docs`, uçları tarayıcıdan denemeye yarayan otomatik belgeyi gösterir.

| Uç | İşlev | Başarı | Hata kodları |
| --- | --- | --- | --- |
| `GET /saglik` | Veritabanına `SELECT 1` gönderir; havuzdan bağlantı için en çok 2 saniye bekler. | `200` `{"durum": "ok"}` | `503` `{"durum": "veritabanına ulaşılamıyor"}`, veritabanına ulaşılamazsa |
| `GET /talepler` | Talepleri en yeniden eskiye, sayfa sayfa listeler; `durum`, `oncelik` ve `etiket` ile süzer, `?ara=` ile başlıkta arar; `?limit=` sayfa boyunu, `?ayrac=` sonraki sayfayı seçer. | `200` | `400` bozuk ayraç, `422` bilinmeyen durum veya öncelik, geçersiz `limit` ya da `ara` |
| `GET /talepler/ozet` | Her durumdaki talep sayısını verir; talebi olmayan durum `0` görünür. | `200` | yok |
| `GET /talepler/{talep_id}` | Tek talebi verir; `ETag` başlığında talebin sürümü bulunur. `If-None-Match` sürümle eşleşirse gövdesiz `304` döner. | `200`, `304` | `404` talep yok, `422` numara pozitif tam sayı değil |
| `POST /talepler` | Yeni talep oluşturur; durum her zaman `acik`, öncelik verilmezse `orta` olur. | `201` | `401` anahtar, `422` geçersiz gövde |
| `PATCH /talepler/{talep_id}` | `If-Match`'teki sürüm güncelse durumu, önceliği ya da ikisini değiştirir. | `200`, yeni `ETag` | `401` anahtar, `428` `If-Match` yok, `400` biçimsiz `If-Match`, `422` geçersiz veya boş gövde, `404` talep yok, `412` sürüm eski |
| `GET /talepler/{talep_id}/yorumlar` | Talebin yorumlarını eklenme sırasıyla listeler. | `200` | `404` talep yok |
| `POST /talepler/{talep_id}/yorumlar` | Talebe `yazan` ve `metin` ile yorum ekler. | `201` | `401` anahtar, `422` geçersiz gövde, `404` talep yok |

### Liste ve Sayfalar

`GET /talepler` bir liste değil, tek bir sayfa döndürür:

```json
{"talepler": [{"id": 12, "baslik": "...", "surum": 1}, ...], "sonraki": "eyJhIjoiMjAyNi0xMC0zMFQwNjowMDowMCswMDowMCIsImkiOjEwfQ"}
```

Talepler en yeniden eskiye, yani açılış zamanına (`acildi`) göre azalan sırada gelir; aynı anda açılmış talepler arasında büyük numara önce gelir. `limit` bir sayfadaki talep sayısıdır: varsayılanı `20`, alabileceği değerler `1`–`100`; aralık dışındaki ya da sayı olmayan bir değer `422` alır.

`sonraki`, sonraki sayfanın nereden başlayacağını gösteren bir ayraçtır; son sayfada `null` olur. Ayraç, istemcinin okuması ya da değiştirmesi için değil, olduğu gibi `?ayrac=` ile geri yollanması için verilir; aynı `durum`, `oncelik`, `etiket`, `ara` ve `limit` değerleriyle birlikte gönderilir. Bu API'nin vermediği ya da bozulmuş bir ayraç `400` alır.

Ayraç bir sayfa numarası değil, sayfanın son talebinin `(acildi, id)` çiftidir; sonraki sayfa bu çiftten küçük olanlarla başlar. Bu yüzden iki sayfa arasında yeni bir talep açılsa da sayfalar kaymaz: hiçbir talep iki kez gelmez, hiçbiri atlanmaz. Yeni talep, listeyi baştan okuyan bir sonraki istekte görünür.

```bash
curl "http://127.0.0.1:8000/talepler?limit=3"
curl "http://127.0.0.1:8000/talepler?limit=3&ayrac=eyJhIjoiMjAyNi0xMC0zMFQwNjowMDowMCswMDowMCIsImkiOjEwfQ"
```

On iki örnek talepte ilk komut 12, 11 ve 10 numaralı talepleri, ikincisi 9, 8 ve 7'yi verir.

### Arama

`ara`, talep başlıklarında PostgreSQL'in Türkçe tam metin aramasıyla arar. Kelimeler köklerine indirilir ve büyük/küçük harfe bakılmaz; `kargom` "Kargo" geçen başlığı, `şifremi` "Şifre" geçen başlığı bulur.

| Yazım | Anlamı |
| --- | --- |
| `kargo numarası` | Boşlukla ayrılan kelimelerin hepsi başlıkta geçmeli. |
| `kargo or şifre` | Kelimelerden biri geçmesi yeter. |
| `kargo -takip` | `takip` geçen başlıklar elenir. |
| `"takip numarası"` | Tırnak içindeki kelimeler bu sırayla, yan yana geçmeli. |

`ve`, `ile`, `için` gibi durak kelimeleri aramaya katılmaz; yalnızca durak kelimesinden oluşan bir arama hata vermez, boş liste döner. `ara` 2–100 karakter olmalıdır; dışındaki değerler `422` alır.

Sonuçlar alakaya göre sıralanmaz; listeyle aynı sırada, en yeniden eskiye gelir ve aynı ayraçla sayfalanır. `ara` öteki süzgeçlerle birlikte kullanılabilir.

```bash
curl "http://127.0.0.1:8000/talepler?ara=fatura"
```

### Sürüm ve Koşullu İstekler

Her talebin bir `surum` sütunu vardır; yeni talep `1` ile başlar ve her başarılı `PATCH` onu bir artırır. `GET /talepler/{talep_id}` bu sürümü tırnak içinde `ETag` başlığında da verir, ör. `ETag: "3"`.

`PATCH`, istemcinin en son okuduğu sürümü `If-Match` başlığında ister. Sürüm kontrolü ile yazma tek bir `UPDATE ... WHERE id = ... AND surum = ...` komutunda yapılır; iki istemci aynı sürümle aynı anda güncellemeye kalkarsa yalnız biri yazar, diğeri `412` alır. Böylece birinin değişikliği farkında olunmadan ezilmez.

| Durum | Yanıt |
| --- | --- |
| `If-Match` yok | `428 Precondition Required`; önce talebi `GET` ile okumak gerekir. |
| `If-Match` tırnaklı tek bir pozitif sayı değil (`1`, `W/"1"`, `*`, `"abc"`, `"0"`, birden çok etiket) | `400 Bad Request` |
| Sürüm güncel değil | `412 Precondition Failed`; hiçbir şey yazılmaz, yanıtın `ETag` başlığı güncel sürümü gösterir. |
| Sürüm güncel | `200 OK`; gövde güncellenen talep, `ETag` yeni sürüm. |

Denetimler şu sırayla yapılır: `401` (API anahtarı), `428`/`400` (`If-Match`), `422` (gövde), `404` (talep), `412` (sürüm). Örneğin anahtarsız ve `If-Match`'siz bir istek `401` alır.

`GET /talepler/{talep_id}`, `If-None-Match` başlığını da okur. İstemci elindeki `ETag`'i bu başlıkla gönderir; talep o sürümdeyse yanıt gövdesiz `304 Not Modified` ve aynı `ETag`'dir, istemci elindeki kopyayı kullanır. Sürüm değişmişse her zamanki gibi `200`, güncel gövde ve yeni `ETag` döner.

Karşılaştırma zayıftır: `W/"3"` ile `"3"` aynı sayılır. Başlık virgülle ayrılmış birden çok etiket taşıyabilir; biri tutarsa `304` döner. `*` her etikete uyar. Talep yoksa başlık ne olursa olsun `404` döner.

```bash
curl -i http://127.0.0.1:8000/talepler/4 -H 'If-None-Match: "1"'   # 304 Not Modified, ETag: "1"
```

### Anahtar ve Gövde

Okuma uçları açıktır. `POST` ve `PATCH` uçları, `X-API-Anahtari` başlığında sunucudaki `API_ANAHTARI` değerinin aynısını ister. Başlık yoksa, değer yanlışsa ya da sunucuda `API_ANAHTARI` hiç tanımlı değilse istek `401` alır ve hiçbir şey değişmez; anahtar ayarlanmamış bir sunucuda yazma tamamen kapalıdır.

Gövdeler Pydantic şemalarıyla doğrulanır. Başlık boşlukları temizlendikten sonra 3–200 karakter, `musteri` tek `@` içeren bir adres, her etiket 1–30 karakter olmalıdır. Şemada bulunmayan bir alan, örneğin oluştururken gönderilen `durum` ya da `id`, sessizce yok sayılmaz; istek `422` ve `extra_forbidden` hatası alır.

```bash
curl -i -X POST http://127.0.0.1:8000/talepler \
  -H "Content-Type: application/json" \
  -H "X-API-Anahtari: gelistirme-anahtari" \
  -d '{"baslik": "Fatura indirilemiyor", "musteri": "ali@example.com", "oncelik": "yuksek", "etiketler": ["fatura"]}'
```

Yanıt `201 Created` ve veritabanının verdiği numara, durum, açılış zamanı ve `surum: 1` ile oluşan talebin JSON'udur.

```bash
curl -i http://127.0.0.1:8000/talepler/4          # ETag: "1"
curl -i -X PATCH http://127.0.0.1:8000/talepler/4 \
  -H "Content-Type: application/json" \
  -H "X-API-Anahtari: gelistirme-anahtari" \
  -H 'If-Match: "1"' \
  -d '{"durum": "kapali"}'
```

İlk `PATCH` `200` ve `ETag: "2"` döner; aynı komut ikinci kez gönderilirse sürüm artık `2` olduğu için `412` alır.

### Yorumlar

Yorumlar `yorumlar` tablosunda tutulur ve `talep_id` ile talebe bağlıdır. Gövde yalnızca `yazan` (1–60 karakter) ve `metin` (1–2000 karakter) alır; boşluklar temizlenir, `talep_id` gibi fazladan bir alan `422` alır. Yanıtta `id`, `talep_id`, `yazan`, `metin` ve veritabanının verdiği `yazildi` zamanı bulunur. Yorum eklemek talebin sürümünü ve `ETag`'ini değiştirmez. Silinen bir talebin yorumları da silinir.

```bash
curl -i -X POST http://127.0.0.1:8000/talepler/4/yorumlar \
  -H "Content-Type: application/json" \
  -H "X-API-Anahtari: gelistirme-anahtari" \
  -d '{"yazan": "ayse", "metin": "Müşteriyi aradım."}'
```
