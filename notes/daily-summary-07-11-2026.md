# 07.11.2026 Gün Sonu Özeti

## Tip İpuçları Çalışma Anında Ne Yapar

Bir parametreye `int` yazmak, Python'un gelen değeri otomatik olarak sayıya çevirmesini veya reddetmesini sağlamıyor. Projede gerçek doğrulamayı model ve argüman ayrıştırıcısı yaparken pyright, kod çalışmadan önce uyumsuz kullanımları buluyor. Tip açıklamalarının araçlar tarafından okunabilmesi ile çalışma anında zorunlu tutulması ayrı şeyler. Bu ayrım [Python typing belgesinde](https://docs.python.org/3/library/typing.html) de açıklanıyor.

## pyright'ın İlk Raporu

İlk pyright çalıştırmasının ham çıktısı depoda kayıtlı olmadığı için başlangıçtaki hata sayısını kesin olarak yazamıyorum. Mevcut değişikliklerde dönüş tipi belirtilmemiş dekoratör, sınıf yerine örnek bekleniyormuş gibi çıkarılan hata parametresi ve `None` olabilen tarihler için düzeltmeler görülebiliyor. Bugünkü doğrulamada `uv run pyright`, sıfır hata, sıfır uyarı ve sıfır bilgi mesajıyla tamamlandı.

## list Yerine Iterable

`kapanmamislar`, `durum_sayilari`, `etiket_gruplari`, `oncelik_sirasi` ve `ara` girdiyi yalnızca dolaştığı için giriş tipleri `Iterable[Talep]` oldu. Böylece liste dışındaki tuple ve üreteçler de sözleşmeye uyuyor; çıktıların liste veya sözlük olması değişmiyor. Bir üretecin tüketildikten sonra başa dönmediğini unutmamak gerekiyor, dolayısıyla `Iterable` birden fazla kez dolaşılabilme garantisi vermiyor.

## Daraltma

`Talep.acildi`, `datetime | None` olduğundan `utcoffset()` çağrısından önce hangi durumda olduğunun anlaşılması gerekiyor. Zaman testlerindeki `assert talep.acildi is not None`, hem testin beklentisini ifade ediyor hem sonraki satır için tipi daraltıyor. PyPI komutunda da `isinstance(sonuc, httpx.HTTPStatusError)` kontrolü hata sonucu ile veri sözlüğünü ayırıyor.

## Generic ve type

`sinirli_topla[T]`, işlerin ürettiği tip ile dönen `list[T]` arasındaki ilişkiyi koruyor. `type PaketSonucu = dict[str, Any] | httpx.HTTPStatusError` ise iki olası sonucu adlandıran bir tip takma adı; JSON içeriğini doğrulayan yeni bir model değil. Ayrıca `type[Exception]` bir hata nesnesini değil hata sınıfını anlatıyor; yeniden deneme ayarına `ConnectionError()` yerine `ConnectionError` veriliyor.

## ParamSpec ile Dekoratör

`yeniden_dene[**P, R]` içindeki `P`, sarılan fonksiyonun konumsal ve anahtar sözcük parametrelerini, `R` ise dönüş tipini taşıyor. `*args: P.args` ve `**kwargs: P.kwargs` sayesinde dekoratör uygulanınca çağrı imzası kaybolmuyor. `functools.wraps` fonksiyon adı gibi bilgileri korurken statik çağrı denetimini tip imzası sağlıyor. `tests/tip_araclar.py`, doğru dönüş tiplerini ve yanlış çağrılarda beklenen hataları denetleyerek bu sözleşmeyi koruyor.

## async def, await ve gather

`async def` fonksiyonunu çağırmak bir coroutine oluşturur; tek başına çağrı işi yürütmeye başlamaz. `await` sonucu beklerken uygun noktalarda başka görevlerin ilerlemesine izin verir; art arda iki `await` yazmak kendiliğinden eşzamanlılık sağlamaz. `asyncio.gather` birden fazla işi birlikte bekler ve sonuçlarını kendisine verilen sırada döndürür. Bu davranışlar [coroutine ve görev belgelerinde](https://docs.python.org/3/library/asyncio-task.html) anlatılıyor.

## Olay Döngüsünü Kilitlemek

Async yeniden deneme yardımcısında `time.sleep` kullanmak aynı olay döngüsündeki diğer görevleri de bekletirdi. Kodun `await asyncio.sleep(bekleme)` kullanması, yeniden deneme aralığında başka işlerin ilerlemesini sağlıyor. `test_async_beklerken_dongu_kilitlenmez`, bekleme sırasında ikinci görevin sayaç artırabildiğini kontrol ediyor; bir fonksiyona yalnızca `async` eklemek içindeki bloklayan işlemleri ortadan kaldırmıyor.

## TaskGroup, İptal ve Zaman Aşımı

`TaskGroup` içindeki bir görev normal bir hatayla başarısız olduğunda diğer görevler iptal edilir ve hatalar grup halinde dışarı taşınır. Varsayılan `gather` davranışı ilk hatayı iletse de diğer işleri aynı biçimde otomatik iptal etmez. `CancelledError`, `BaseException` ailesindedir; yeniden denemenin `(Exception,)` filtresine takılmaz. `asyncio.timeout` ise kendi başlattığı iptali bağlamın dışında yakalanabilen `TimeoutError` olarak bildirir. Ayrıntılar [TaskGroup ve zaman aşımı belgelerinde](https://docs.python.org/3/library/asyncio-task.html#task-groups) bulunuyor.

## sinirli_topla ve yeniden_dene_async

`sinirli_topla`, hazır coroutine'ler yerine çağrılınca beklenebilir iş üreten fonksiyonlar alıyor ve işi semafor izni alındıktan sonra başlatıyor. Görevler `TaskGroup` içinde tutuluyor; sonuçlar görevlerin oluşturulma sırasıyla toplanıyor. `yeniden_dene_async`, yalnızca seçilen hata sınıflarını yakalıyor, denemeler arasında async bekliyor ve son hatayı yeniden yükseltiyor. Yeniden deneme boyunca semafor izni elde tutulduğu için `en_fazla`, yalnızca o anda veri aktaran bağlantıların değil yürütülen paket işlerinin de sınırı oluyor.

## Eşzamanlı PyPI

Paket sorguları ortak bir `httpx.AsyncClient` kullanıyor ve varsayılan olarak en fazla dört paket işi birlikte yürütülüyor. `uv run yardim-masasi -e 2 httpx fastapi rich` bu sınırı ikiye indiriyor; çıktı yine verilen paket sırasını koruyor. 404 ve diğer HTTP durum hataları sonuç olarak taşınıyor, böylece başarılı paketler de yazılabiliyor. Taşıma hatası üç denemede de sürerse komut kalan işleri iptal ederek çıkış kodu 1 ile bitiyor; kullanım hatalarının kodu 2 oluyor.

## Ölçüm

Bugün `time.perf_counter()` ile her biri `asyncio.sleep(0.05)` kullanan sekiz işi ölçtüm. `en_fazla=1` için 0,401 saniye, `en_fazla=4` için 0,101 saniye geçti ve iki durumda da sekiz sonuç döndü. Bunlar kontrollü bekleme ölçümleri; gerçek PyPI hızını veya her makinede aynı süreyi vaat etmiyor. Büyük listelerde sıra bekleme, en yavaş yanıt ve yeniden denemeler toplam süreyi etkiliyor; tek ölçüm yerine tekrarlı ölçümler daha sağlam karşılaştırma sağlar.

## xargs -P

`printf '%s\n' httpx fastapi rich | xargs -n 1 -P 2 uv run yardim-masasi`, paket başına ayrı süreç başlatıp aynı anda en fazla iki süreci yürütmek için kullanılabilir. Uygulamanın `-e` seçeneği ise tek süreçte ortak istemciyle sorgu yapar. Ayrı süreçlerin çıktıları giriş sırasını korumayabilir ve istemci bağlantılarını paylaşmaz. Bu yüzden `xargs -P` ile komut içindeki eşzamanlılık sınırı aynı çalışma düzeni değildir.

## Araştırma Notları

README'deki varsayılanı ve hata kodlarını `src/yardim_masasi/__init__.py`, yeniden deneme davranışını `pypi.py` ve `eszamanli.py` üzerinden kontrol ettim. `tests/test_cli.py`, `tests/test_pypi_async.py` ve `tests/test_eszamanli.py` gerçek ağa ihtiyaç duymadan sıralama, hata, iptal ve eşzamanlılık sınırını doğruluyor. Gün sonu kontrolünde `uv run --locked pytest -q` sonucu 200 başarılı test oldu. Gereksiz bastırma yorumlarını hata sayan ayarın anlamını [pyright yapılandırma belgesinden](https://github.com/microsoft/pyright/blob/main/docs/configuration.md) kontrol ettim; yerel ayar `src` ve `tests` dizinlerini kapsıyor.

## TypeScript'ten Farklı Üç Şey

Birinci fark, Python'da async fonksiyon çağrısının yürütülmeyi bekleyen coroutine üretmesi; JavaScript/TypeScript'te async fonksiyon gövdesinin ilk bekleme noktasına kadar çağrı sırasında ilerlemesidir. Bu başlangıç davranışı [JavaScript async function belgesinde](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function#description) açıklanıyor. İkinci fark, Python'daki `type[Exception]` ifadesinin sınıf nesnesini anlatması; TypeScript'te kurucu tarafının genellikle `typeof` veya bir kurucu imzasıyla belirtilmesidir. Sınıf ve kurucu tiplerinin ayrımı [TypeScript sınıf belgesinde](https://www.typescriptlang.org/docs/handbook/2/classes.html#abstract-construct-signatures) örnekleniyor. Üçüncü fark, Python tip açıklamalarının çalışma anında araçlarca incelenebilmesi, TypeScript tip açıklamalarının ise JavaScript çıktısından silinmesidir. İki dilde de statik tip açıklaması dışarıdan gelen JSON'u kendiliğinden doğrulamaz.

## Yanıldığım İki Tahmin

Bu bölüm kişisel geçmiş iddiası değil, bugünkü örneklerden çıkarılmış iki yanlış varsayımın değerlendirmesidir. İlk varsayım, async fonksiyonları çağırıp bir listeye koymanın onları hemen çalıştıracağıydı; coroutine'leri beklemek veya görev olarak planlamak gerektiğini ayırmak gerekiyor. İkinci varsayım, hızlı dönen paketin önce yazılacağıydı; mevcut uygulama bütün sonuçları bekliyor ve giriş sırasıyla yazıyor. Testlerde gecikmeleri farklı tutmak, tamamlanma sırası ile sonuç sırasının ayrı olduğunu görünür kılıyor.

## En Çok Zorlandığım Konu

Bu çalışma için en zorlayıcı kavramsal ayrım, yeniden denenebilir ağ hatası ile görev iptalini aynı şey saymamaktı. Yeniden deneme bir işi sürdürmeye çalışırken iptal o işi durdurma isteği taşıyor. `test_async_iptal_yeniden_denenmez` ile hata halinde diğer görevlerin durmasını denetleyen testleri birlikte okumak bu ayrımı somutlaştırıyor. Bu değerlendirme, mevcut kod ve testlerden hazırlanmış öğrenme notudur.
