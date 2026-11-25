[← README'ye dön](../README.tr.md)

# Bilinen Sınırlamalar

- `yardim-masasi` günlük ayarı yapmaz. Başka bir günlük yapılandırması yoksa yeniden deneme uyarıları ve son hata, logging'in yedek işleyicisiyle stderr'e zaman, seviye ve kaydedici adı olmadan çıplak mesaj olarak yazılır.
- Büyük paket listelerinde bütün sonuçlar beklendiğinden toplam süre en yavaş yanıta da bağlıdır. Eşzamanlılık sınırı yüzünden sırada bekleyen işler ve yeniden denemeler bu süreyi uzatır; hızlı biten paketler hemen gösterilmez.
- `PYPI_ZAMAN_ASIMI` sayıya çevrilemiyorsa `ValueError` oluşur. Değer aralığı için ayrıca doğrulama yapılmaz.
- PyPI sorguları için önbellek bulunmaz.
- Bağımlılıklar için otomatik güvenlik açığı taraması yapılandırılmamıştır.
- Varsayılan `ornek/talepler.json` yolu komutun çalıştırıldığı klasöre göredir; proje kökünden başka bir klasörde "dosya bulunamadı" der.
- Talep dosyası UTF-8 değilse düzgün bir mesaj yok; Python'un hata izi basılır.
- API çalışırken veritabanı kapanırsa havuzdaki kopuk bağlantıyı alan ilk istek hemen hata alır. Sonraki isteklerde yalnızca `/saglik` en çok 2 saniye bekleyip `503` döner; öbür uçlar havuzun 30 saniyelik zaman aşımına kadar bekler ve sonra `500` alır. Veritabanı geri geldiğinde havuzun yeniden bağlanma süresi sabit değildir; istekler birkaç saniye daha hata alabilir.
- Kapta tek bir uvicorn süreci çalışıyor; birden çok işçi ya da kopya yok.
- `migrate` her `docker compose up`'ta çalışıyor. Aynı veritabanına iki yerden aynı anda `up` yapılırsa migration'lar birbiriyle yarışabilir.
- Taban imajlar (`python:3.15-slim`, `ghcr.io/astral-sh/uv:0.13.7`, `postgres:18-alpine`) etiketle seçiliyor, özetle (`@sha256:...`) sabitlenmiyor; aynı etiket zamanla başka bir imajı gösterebilir. İmaj güvenlik açıklarına karşı taranmıyor.
- API anahtarı tek ve herkesin paylaştığı bir değer. Kullanıcı ayrımı yok; bir talebi kimin oluşturduğu ya da değiştirdiği kaydedilmiyor. Anahtarı değiştirmek sunucuyu yeni ortam değişkeniyle yeniden başlatmayı gerektiriyor.
- Migration'lar elle yazılıyor. Tablolar SQLAlchemy modeliyle tanımlanmadığı için `alembic revision --autogenerate` kullanılamıyor; şema ile revizyonların uyumunu yalnızca testler denetliyor.
- `If-Match` yalnızca tek ve tırnaklı bir sürüm kabul ediyor. `*`, zayıf etiket (`W/"1"`) ve virgülle ayrılmış birden çok etiket standartta geçerli olsa da `400` alıyor.
- Yorumlar düzenlenemiyor ve silinemiyor. `yazan` alanı istemcinin yazdığı serbest bir metin; API anahtarı ortak olduğu için yorumu gerçekten kimin yazdığı doğrulanmıyor.
- Sayfalar yalnızca ileri gidiyor: önceki sayfaya dönmek ya da belli bir sayfaya atlamak için ayraç yok. Yanıtta toplam talep ya da sayfa sayısı da yok.
- Arama yalnızca başlıkta yapılıyor; yorumlar ve etiketler aranmıyor. Sonuçlar alakaya göre değil, en yeniden eskiye sıralanıyor.
- Türkçe kök bulucu bazı ekli kelimeleri yalın hâlleriyle eşleştiremiyor: `fatura` ile `faturada` (`fatur` / `fatura`), `numara` ile `numarası` (`numar` / `numaras`), `iade` ile `iadem` (`ia` / `iade`) farklı köklere iniyor, biri ötekini bulmuyor. Yazım hatalarına tolerans yok; `fatüra` hiçbir şey bulmaz.
- Büyük `I` harfi Türkçe kurala göre `ı`'ya değil `i`'ye küçültülüyor: `IŞIKLI` `işikli` olarak saklanıyor, bu yüzden `ışıklı` aramasıyla bulunmuyor.
