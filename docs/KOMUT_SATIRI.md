[← README'ye dön](../README.tr.md)

# Komut Satırı Araçları

## PyPI Sorgusu

`yardim-masasi [-h] [-e N] PAKET [PAKET ...]`, en az bir paket adı ister.
`-e N` veya `--eszamanli N`, aynı anda yürütülen sorguların üst sınırını
belirler; varsayılanı **4** olan bu değer pozitif tam sayı olmalıdır.
`-e 1` sorguları sırayla yürütür; `-e 2` en fazla iki sorguyu birlikte yürütür.

İstekler ortak bir `httpx.AsyncClient` ile yapılır. Sonuçlar bütün işler
tamamlandıktan sonra, yanıtların geliş sırasına göre değil komutta verilen
paket sırasıyla yazılır. Paket özetleri stdout'a, hata mesajları stderr'e
gider; bu iki akışı birleştiren araçların ekrandaki sıralaması tamponlama
nedeniyle farklı görünebilir.

Bağlantı ve zaman aşımı gibi taşıma hataları yarım saniye arayla iki kez
daha denenir; ilk istekle birlikte toplam üç deneme yapılır. HTTP 404 ve
diğer HTTP durum hataları yeniden denenmez. Bulunamayan paket diğer paketlerin
özetlerini engellemez; taşıma hatası son denemede de sürerse kalan işler
iptal edilir ve paket özetleri basılmadan komut hata mesajıyla sonlanır.

| Çıkış kodu | Anlamı |
| --- | --- |
| `0` | Bütün paketler başarıyla sorgulandı veya yardım gösterildi. |
| `1` | Paket bulunamadı (404), başka bir HTTP durum hatası oluştu veya yeniden denemelere rağmen PyPI'a ulaşılamadı. |
| `2` | Kullanım hatası: paket adı eksik, bilinmeyen bayrak veya geçersiz/eksik `-e` değeri. |

Bu ağ ve HTTP hataları hata izi yerine kısa mesajlarla bildirilir. Kullanım
hatalarında `argparse` kullanım özetini ve açıklamayı stderr'e yazar.

## Komut Satırı

`uv run talep-ozeti --help` çıktısının özeti:

```text
talep-ozeti [-h] [--durum {acik,beklemede,kapali}]
           [--oncelik {yuksek,orta,dusuk}] [--etiket ETIKET]
           [--son-gun N] [-v] [--version] [dosya]
```

İsteğe bağlı `dosya`, okunacak `.json` veya `.jsonl` dosyasıdır; verilmezse
çalışma klasörüne göre `ornek/talepler.json` kullanılır.

| Bayrak | İşlev | Örnek komut |
| --- | --- | --- |
| `-h`, `--help` | Yardımı gösterir ve çıkar. | `uv run talep-ozeti -h` veya `uv run talep-ozeti --help` |
| `--durum` | `acik`, `beklemede` veya `kapali` durumunu seçer. | `uv run talep-ozeti --durum kapali` |
| `--oncelik` | `yuksek`, `orta` veya `dusuk` önceliğini seçer. | `uv run talep-ozeti --oncelik yuksek` |
| `--etiket` | Verilen etiketi tam olarak taşıyan talepleri seçer. | `uv run talep-ozeti --etiket hesap` |
| `--son-gun N` | Son N günlük alt zaman sınırını uygular; N pozitif tam sayı olmalıdır. | `uv run talep-ozeti ornek/talepler-zamanli.jsonl --son-gun 10` |
| `-v`, `--ayrintili` | DEBUG günlüklerini açar. | `uv run talep-ozeti -v` veya `uv run talep-ozeti --ayrintili` |
| `--version` | Kurulu paketin sürümünü gösterir ve çıkar. | `uv run talep-ozeti --version` |

Filtreler birlikte uygulanır; örneğin `uv run talep-ozeti --oncelik yuksek --etiket hesap`
iki koşulu da sağlayanları seçer. Sayımlar filtrelenmiş bütün talepleri içerir;
liste, `--durum` verilmedikçe yalnızca kapanmamış talepleri gösterir.
`--durum kapali` kapalı talepleri de listeler. Hiç eşleşme yoksa sayımlar sıfırdır
ve komut başarıyla biter; yardım ve sürüm seçenekleri talep dosyasını okumaz.

| Çıkış kodu | Anlamı | Örnek durum |
| --- | --- | --- |
| `0` | Başarı | Özet, yardım veya sürüm yazıldı. |
| `1` | Talep hatası | Dosya okunamadı ya da bir talep doğrulanamadı. |
| `2` | Kullanım hatası | Bilinmeyen bayrak, geçersiz seçenek değeri, eksik bayrak değeri veya birden fazla dosya verildi. |

Talep hataları tek satırlık mesajla stderr'e yazılır. Kullanım hatalarında
`argparse` kullanım özetini ve hata açıklamasını stderr'e yazar.

## Günlük Kayıtları

`talep-ozeti` için `-v` veya `--ayrintili`, günlük seviyesini DEBUG yapar; dosyadan okunan ve
filtrelerden sonra kalan talep sayıları görünür. Bayrak verilmezse seviye
WARNING'dir. `yeniden_dene` yardımcısı yeniden denenecek hataları WARNING,
son denemedeki hatayı ERROR seviyesinde kaydeder; bu kayıtlar ilgili işlem
çalıştığında oluşur.

`yardim-masasi` artık async istekleri ve `yeniden_dene_async` dekoratörünü
kullanır; PyPI yeniden deneme kayıtları **`yardim_masasi.eszamanli`**
kaydedicisinden gelir. Burada da yeniden denenecek hata WARNING, son hata
ERROR seviyesindedir. Senkron `yeniden_dene` kayıtları ise
`yardim_masasi.araclar` adını kullanmaya devam eder.

Özet stdout'a, günlükler stderr'e gider. Böylece özeti başka bir komuta veya
dosyaya aktarırken tanılama mesajları sonuç verisine karışmaz. Kütüphane
modülleri `logging.getLogger(__name__)` ile kayıt üretir; seviye ve biçimi
`talep-ozeti` girişindeki `logging.basicConfig` belirler.

Bash'te özeti ve günlükleri birlikte ekranda görmek ve dosyaya kaydetmek için:

```bash
set -o pipefail
uv run talep-ozeti ornek/talepler-zamanli.jsonl --son-gun 10 -v 2>&1 | tee talep-ozeti.log
```

`2>&1`, stderr'i stdout'un gittiği yere yönlendirir; `tee` birleşen akışı hem
terminale hem dosyaya yazar. `tee` dosyayı yeniden yazar; ekleme için
`tee -a talep-ozeti.log` kullanılır. `pipefail`, soldaki komut başarısızken
`tee` başarılı diye boru hattının başarılı görünmesini önler; Bash bu ayarla
en sağdaki başarısız komutun çıkış kodunu döndürür.

## Talep Dosyası

Bir JSON listesi (`.json`) ya da her satırında bir talep olan bir JSON Lines dosyası (`.jsonl`). Hangisi olduğu dosyanın uzantısından anlaşılır; `.jsonl` dosyasındaki boş satırlar atlanır. Her talep şu alanları taşır:

    id          sayı
    baslik      metin
    durum       acik, beklemede, kapali
    oncelik     yuksek, orta, dusuk
    etiketler   metin listesi (boş olabilir)
    musteri     e-posta adresi
    acildi      isteğe bağlı, saat dilimi içeren ISO 8601 tarih-saat metni

`id`, `baslik`, `durum`, `oncelik` ve `musteri` zorunlu; `etiketler` yazılmazsa boş sayılır. `id` pozitif bir tam sayıdır ve dosyada bir kez geçer. `musteri` `@` içerir. Fazladan alanlar yok sayılır.

## Zamanlı Talepler

`acildi` alanı, `2026-11-02T09:30:00+03:00` gibi ISO 8601 tarih-saat metnidir.
`+03:00`, UTC'ye göre üç saat ileriyi belirtir; aynı an UTC olarak
`2026-11-02T06:30:00Z` şeklinde de yazılabilir. Saat dilimi zorunludur:
`2026-11-02T09:30:00` gibi ofsetsiz bir değer geçersiz talep sayılır ve komut
`1` koduyla biter. Alan yazılmazsa veya `null` ise modelde `None` olur;
eski talep dosyaları okunmaya devam eder.

[ornek/talepler-zamanli.jsonl](../ornek/talepler-zamanli.jsonl), her satırında
`acildi` alanı bulunan toplam on iki örnek talep içerir:

```bash
uv run talep-ozeti ornek/talepler-zamanli.jsonl --son-gun 10
```

`--son-gun 10`, çalıştırma anından on günlük süreyi çıkarıp bir alt sınır
hesaplar; bu sınırdaki ve daha yeni talepleri tutar. Bu bir takvim günü
başlangıcı hesabı değildir. Zamanı olmayan talepler bu filtrede elenir;
zaman filtresi verilmezse korunur. Mevcut filtre gelecekteki tarihlere üst
sınır koymaz. Örnekteki tarihler sabit olduğu için aynı komutun sonucu
çalıştırıldığı güne göre değişir; bütün tarihler eskidiğinde sıfır sayımları
normaldir.
