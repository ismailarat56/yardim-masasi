# 31.10.2026 Gün Sonu Özeti

Taslak notu: Kişisel tahmin ve zorlanma bölümleri, kendi deneyimime göre uyarlayabileceğim örnek anlatımlardır.

## Modül ve import

Bir Python dosyası kendi ad alanına sahip bir modül olarak kullanılabiliyor; import ile o modüle veya içindeki isimlere erişiyorum. Modülün üst seviyesindeki işlemler ilk yüklemede çalışıyor, sonraki olağan import işlemleri önbellekteki modülü kullanıyor. Bu nedenle yalnızca içe aktarılınca ağ isteği yapmak gibi yan etkileri üst seviyeye koymamak gerekiyor.

## Paket, src Düzeni ve python -m

Bu projede `__init__.py`, paket girişini; `src` klasörü ise dağıtılan Python kodunun proje dosyalarından ayrılmasını sağlıyor. src düzeninde paketi ortama kurmak, import işlemlerinin proje köküne tesadüfen bağlı kalmasını önlüyor. `python -m yardim_masasi`, paketin `__main__.py` dosyasını çalıştırarak mevcut komut girişine ulaşıyor.

## Döngüsel İçe Aktarma

İki modül birbirini yüklemeye çalışırsa henüz tanımlanmamış bir isme erişilebiliyor ve kısmen yüklenmiş modül hatası oluşabiliyor. Ortak parçaları daha alt seviyede bir modüle taşımak bağımlılığın yönünü sadeleştiriyor. Burada akış yardımcılarının talep modelini bilmemesi, modelin onları kullanabilmesini kolaylaştırıyor.

## Yineleyici ve Üreteç

Yinelenebilir bir nesneden `iter` ile yineleyici alıyorum; `next` her çağrıda sıradaki öğeyi getiriyor ve öğeler bitince `StopIteration` oluşuyor. İçinde `yield` bulunan fonksiyon ise çağrıldığında gövdesini hemen tamamlamak yerine bir üreteç döndürüyor. Üreteç kaldığı yerden devam eden bir yineleyici olduğu için tüketildikten sonra baştan dolaşmak için yenisini oluşturmam gerekiyor.

## Üreteç İfadesi ve Tembellik

Üreteç ifadesi, sonuçların tamamını baştan bir listeye doldurmak yerine ihtiyaç oldukça hesaplıyor. Bu yaklaşım ara sonuçlar için bellek kullanımını azaltabiliyor, fakat hesaplama sırasında doğacak hataları da tüketim anına erteliyor. Sonuçları listeye çevirdiğim noktada bütün öğelerin üretilmesini istemiş oluyorum.

## with ve Bağlam Yöneticisi

`with`, bir kaynağa giriş ve çıkış işlemlerini bağlam yöneticisine bırakıyor; dosya okurken bloktan çıkıldığında dosyanın kapanmasını sağlıyor. Blok içinde hata veya erken dönüş olması da çıkış işlemini atlamıyor. Bir üreteç `with` içinde askıda kalırsa dosya da açık kalabileceğinden, üretecin tükenmesi veya kapatılması kaynak ömrü açısından önemli.

## Dekoratör

Dekoratör, bir fonksiyonu alıp ek davranış taşıyan başka bir çağrılabilir nesneyle sarmalamamı sağlıyor. Parametreli dekoratörde önce ayarları alan dış fonksiyon, sonra asıl fonksiyonu alan dekoratör, en içte de çağrıyı yöneten sarmalayıcı bulunuyor. `functools.wraps`, sarmalanan fonksiyonun adı ve açıklaması gibi bilgileri koruyor.

## akis.py

Akış modülü, boş olmayan satırları gerçek satır numaralarıyla üretme, JSON Lines çözme ve öğeleri parçalara ayırma işlerini topluyor. JSON hatasında satır ve sütun bilgisini taşıyor; talebe özgü alan doğrulamasını model üstleniyor. Parçalara bölmede son grup belirtilen boyuttan küçük kalabiliyor ve boyutun pozitif olması baştan denetleniyor.

## JSON Lines

JSON Lines biçiminde her dolu satır ayrı bir JSON değeri taşıyor; bu projede her değerin bir talep nesnesi olması bekleniyor ve boş satırlar atlanıyor. Okuma yardımcısındaki `try` içinde `return jsonl_oku(yol)` yazınca yalnızca üreteç dönüyordu; dosya veya JSON hatası daha sonra tüketim sırasında doğduğu için o `except` bloklarına ulaşmadan hata izi basılıyordu. Üreteci aynı `try` içinde listeye çevirmek hatayı dosya hatasına dönüştürmeyi sağlıyor, ancak bu noktada bütün kayıtlar belleğe alınıyor.

## yeniden_dene

Bu dekoratör yalnızca seçilen hata türlerinde çağrıyı tekrarlıyor, başarılı sonuç alındığında hemen dönüyor ve son başarısızlıkta hatayı yeniden yükseltiyor. PyPI çağrısında toplam üç deneme var; ilk iki başarısız denemeden sonra yarım saniye bekleniyor. Paket bulunamadığında oluşan HTTP durum hatası, yeniden denenen taşıma hataları arasında bulunmuyor.

## head, tail ve Boru Hattı

`head` çıktının başını, `tail` sonunu görmemi sağlıyor; satır sayısını seçerek uzun sonuçları daraltabiliyorum. Boru hattındaki `|`, soldaki komutun standart çıktısını sağdakinin standart girdisine bağlıyor, standart hata ise ayrıca yönlendirilmedikçe terminalde kalıyor. Bu yüzden hata mesajının borudan geçen normal veriyle aynı yerde görünmesini beklememeliyim.

## TypeScript'ten Farklı Çıkan Üç Şey

- Bir modülden isim almak Python'da `from yardim_masasi.metin import temizle`, TypeScript'te dışa aktarılmış bir fonksiyon için `import { temizle } from "./metin"` şeklinde yazılıyor; TypeScript tarafında modül yolunun ayrıntıları proje ayarına bağlı.
- Sıradaki öğeyi Python'da `next(akim)`, TypeScript'te `akim.next()` ile alıyorum; Python bitişte `StopIteration` üretirken TypeScript tarafında sonuç nesnesinin `done` alanına bakıyorum.
- Bir fonksiyonu sarmalayıcıyla değiştirmek Python'da `islem = sar(islem)`, TypeScript'te yeniden atanabilir bir bağ için `islem = sar(islem)` olarak yazılabiliyor; Python ayrıca fonksiyon tanımının üstünde `@sar` kısayolunu sunarken TypeScript'in dekoratör sözdizimi sıradan fonksiyon bildirimlerine uygulanmıyor.

## Yanıldığım İki Tahmin

İlk tahminim, üreteç fonksiyonunu çağırınca dosyanın hemen okunacağıydı; okumanın ilk öğe istendiğinde başladığını ayırt etmem gerekti. İkinci tahminim, üreteci bir `try` içinden döndürmenin okuma hatalarını da yakalayacağıydı; hatayı yakalayacak kapsamın tüketim anını kapsaması gerektiğini gördüm.

## En Çok Zorlandığım Konu

En çok zorlandığım konu, üretecin oluşturulduğu an ile iş yaptığı anı ayrı düşünmek oldu. Dosyanın açılmasını, öğelerin üretilmesini ve hatanın yakalanmasını aynı zaman çizgisinde izlemek, JSON Lines hata akışının neden değiştiğini anlamamı sağladı.
