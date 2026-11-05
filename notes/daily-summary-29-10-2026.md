# 29.10.2026 Gün Sonu Özeti

Taslak notu: Kişisel tahmin ve zorlanma bölümleri, kendi deneyimime göre uyarlayabileceğim örnek anlatımlardır.

## İsim, Nesne ve Kopya

Python'da atama nesneyi kopyalamıyor; bir ismi o nesneye bağlıyor, bu yüzden iki isim aynı listeyi gösterebiliyor. Yüzeysel kopya dış koleksiyonu ayırıyor ama içindeki değişebilir nesneler ortak kalabiliyor. İç içe verileri de ayırmam gerektiğinde derin kopyanın neyi çoğalttığını düşünmem gerekiyor.

## Kapsam: global ve nonlocal

Bir fonksiyon içinde bir isme değer atadığımda o isim normalde yerel kabul ediliyor. `global`, modül kapsamındaki isme yeniden atama yapmamı; `nonlocal` ise dıştaki bir fonksiyonun mevcut yerel ismini yeniden bağlamamı sağlıyor. Bir listeyi yerinde değiştirmekle o listeyi tutan isme başka bir nesne atamak aynı işlem değil.

## Sınıf Özniteliği ve Nesne Özniteliği

Sınıf özniteliği ortak tanımlanıyor; nesne üzerinde aynı adla bir değer oluşturursam o nesne için sınıftaki değeri gölgeliyorum. Sınıfa konan değişebilir bir listeyi yerinde değiştirmek, o listeye erişen diğer nesneleri de etkiliyor. Her nesneye ayrı veri gerektiğinde başlangıç sırasında nesne özniteliği oluşturmak daha uygun.

## Üç Metot Türü

Örnek metodu `self` ile belirli bir nesnenin verisine, sınıf metodu `cls` ile çağrıldığı sınıfa erişiyor. Statik metot ise nesneyi veya sınıfı otomatik parametre olarak almıyor; sınıfla ilişkili bir yardımcı işlem olarak duruyor. Alternatif bir kurucu için sınıf metodunu seçmek, alt sınıftan çağrıldığında doğru türde nesne üretmeyi de kolaylaştırıyor.

## property ve Alt Çizgili Adlar

`property`, hesaplanan bir değeri alan okur gibi kullanmamı sağlıyor; depodaki açık talep sayısı buna örnek. Tek alt çizgi, adın iç kullanım için olduğunu belirten bir anlaşma, erişim engeli değil. Başında çift alt çizgi olan adlarda isim dönüştürme uygulanıyor; bu da tam gizlilikten çok alt sınıflardaki isim çakışmalarını azaltıyor.

## Eşitlik ve hash

Eşitlik değerlerin aynı kabul edilmesini, `is` ise iki ismin aynı nesneyi gösterip göstermediğini sorguluyor. Eşit kabul edilen iki nesnenin hash değerleri de aynı olmalı; ters yönde böyle bir garanti yok. Talep modelindeki donmuş dataclass ve hashlenebilir alanlar, talepleri kümede veya sözlük anahtarı olarak kullanmaya elverişli kılıyor.

## Sıralama, Toplama ve Kapsayıcı Metotları

Sıralama için bir anahtar fonksiyonuyla karşılaştırılacak değeri seçebiliyorum; kendi türümde doğrudan karşılaştırma istiyorsam `__lt__` gibi metotlar devreye giriyor. Toplama davranışını `__add__` belirliyor; `sum` varsayılan olarak sıfırdan başladığı için özel nesnelerde başlangıç değerini ve ters toplama davranışını da düşünmek gerekiyor. `__len__`, `__contains__` ve `__getitem__` ise uzunluk, üyelik ve köşeli parantezle erişimin anlamını tanımlıyor.

## Duck Typing, ABC ve Protocol

Duck typing yaklaşımında nesnenin soyundan çok ihtiyaç duyduğum işlemi yapabilmesi önemli. ABC ile ortak bir soyut sözleşme kurup eksik soyut metotları olan sınıfların oluşturulmasını engelleyebiliyorum. Protocol ise özellikle statik tip denetiminde, aynı üst sınıftan gelmeden gerekli üyeleri sağlayan türleri ifade etmeme yarıyor.

## TalepDeposu

TalepDeposu talepleri kimlikleriyle bir sözlükte saklıyor ve sözlüğün ekleme sırasını korumasından yararlanıyor. `__iter__` yokken `for`, eski dizi protokolüne dönüp `__getitem__(0)` ile başlamayı denediği için, kimlik olarak 0 bulunamayınca `KeyError: 0` oluşuyordu; bu yol bitiş için `IndexError` bekliyor. `__iter__` ile sözlüğün değerlerini dolaştırınca döngü kimliklere indeks muamelesi yapmak yerine talepleri sırayla alıyor.

## diff ile Davranışı Korumak

Bir düzenlemeden önce ve sonra aynı girdinin çıktısını kaydedip `diff` ile karşılaştırmak, görünen davranışın değişip değişmediğini gösteriyor. Çıktıların aynı olması yalnızca denenen örnek için kanıt sağlıyor; hata mesajları, çıkış kodları ve başka girdiler ayrıca kontrol edilmeli. Böylece iç düzeni değiştirirken kullanıcıya yansıyan farkları daha kolay yakalayabiliyorum.

## TypeScript'ten Farklı Çıkan Üç Şey

- Nesne kimliğini Python'da `a is b`, TypeScript'te nesneler için `a === b` ile karşılaştırıyorum; Python'daki `==` ise sınıfın değer eşitliği davranışını kullanabiliyor.
- Bir listenin yüzeysel kopyasını Python'da `kopya = liste.copy()`, TypeScript'te `const kopya = [...liste]` ile alıyorum; iki dilde de içteki nesneler ortak kalabiliyor.
- Bir eşlemede anahtar varlığını Python'da `numara in kayitlar`, TypeScript'te bir Map için `kayitlar.has(numara)` ile sorguluyorum; Python'da özel kapsayıcılar bu işlemi `__contains__` ile tanımlayabiliyor.

## Yanıldığım İki Tahmin

İlk tahminim, bir listeyi başka bir isme atayınca bağımsız bir kopya oluşacağıydı; ortak nesneyi değiştirmek iki isimden de görülebiliyor. İkinci tahminim, köşeli parantezle erişim sunan deponun döngüde doğrudan talepleri vereceğiydi; Python'un sıfırdan indeks denemesiyle kimliğe göre erişimin çakıştığını fark ettim.

## En Çok Zorlandığım Konu

En çok zorlandığım konu, özel metotların hangi dil işlemi tarafından çağrıldığını birbirinden ayırmak oldu. Depoyu bir sözlük gibi kimlikle sorgulamak ile içindeki talepleri sırayla dolaşmak için ayrı davranışlar tanımlamam gerektiğini görmek konuyu netleştirdi.
