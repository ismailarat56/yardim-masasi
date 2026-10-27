# 27.10.2026 Gün Sonu Özeti

Taslak notu: Bu özet mevcut proje kodu ve testlerinden hareketle hazırlandı; kişisel tahminler ve zorlanma anlatımları, gerçek çalışma deneyimine göre uyarlanabilecek örneklerdir.

## REPL

REPL, küçük bir ifadeyi yazıp sonucunu hemen görebildiğim etkileşimli Python ortamı. Bir metin işleminin ya da koşulun davranışını burada deneyerek anlamak, bütün programı çalıştırmadan düşüncemi kontrol etmemi sağlıyor.

## Tipler ve Doğruluk Değeri

Bir değerin tipi ile koşul içinde doğru kabul edilmesi farklı şeyler; boş liste, boş metin, sıfır ve None yanlış kabul ediliyor. İçinde yalnızca boşluk bulunan metin ise boş olmadığı için doğru sayılıyor, bu yüzden etiketleri süzmeden önce boşlukları temizlemek gerekiyor.

## String ve Türkçe Harfler

Metinler değiştirilemediği için harf dönüştürme ve boşluk temizleme işlemleri yeni bir metin üretiyor. Standart küçük harf dönüşümü Türkçedeki İ ve I ayrımını istediğim gibi ele almadığından önce bu harfleri eşlemek gerekiyor. İsmail adının dönüşümden sonra altı karakter kalmasını denetleyen test, görünüşü benzer bir sonucun uzunluğunun farklı olabileceğini gösteriyor.

## Liste ve Tuple

Listeye eleman ekleyip çıkarabiliyorum; tuple ise elemanlarının yerlerini veya tuttuğu referansları değiştirmeme izin vermiyor. E-posta adresini ayırırken oluşan üç parçalı tuple'ı üç değişkene açmak, her parçanın görevini daha kolay görmemi sağlıyor.

## Sözlük ve Küme

Sözlük, talebin alanlarını adlarıyla tutmak ve etiketlere bağlı talep numaralarını gruplamak için uygun. Küme tekrarları kaldırıyor ama ilk görülme sırasını garanti etmiyor; etiketlerde bu sıra gerektiği için sözlüğün eklenme sırasını korumasından yararlanıyorum.

## Döngüler ve Kavrayışlar

Kapanmamış talepleri seçmek gibi tek bir filtreyi liste kavrayışıyla kısa ve anlaşılır biçimde anlatabiliyorum. Etiketleri gruplamak ya da birden fazla koşulla aramak gerektiğinde açık bir döngü adımları takip etmeyi kolaylaştırıyor. Durum sayılarını oluştururken her durum için eşleşen kayıtları sayıp sonucu sözlükte topluyorum.

## Fonksiyonlar ve Argümanlar

Parametre fonksiyonun tanımındaki isim, argüman ise çağırırken verdiğim değer. Arama fonksiyonu değişken sayıda kelime alırken durum filtresini yalnızca adıyla kabul ediyor; böylece arama kelimeleriyle filtre birbirine karışmıyor. Tip ipuçları beklenen girdiyi anlatıyor, fakat tek başına çalışma sırasında doğrulama yapmıyor.

## Kendi Yazdığım Fonksiyonlar

En çok uğraştığım fonksiyon olarak kisalt'ı seçiyorum; hem uzunluk sınırını korumak hem de sonuna tek karakterlik üç nokta eklemek dikkat istiyor. Özellikle test_kisalt_kesilen_yerdeki_boslugu_atar testi, sekiz karakterlik sınırda “Fatura…” sonucunu bekleyerek kesimin sonundaki boşluğu da temizlemem gerektiğini gösteriyor. Farklı sınırları deneyen test ise sonucun hiçbir zaman verilen sınırdan uzun olmamasını kontrol ediyor.

## sort ve uniq

Terminalde sort satırları sıralarken uniq yalnızca yan yana duran tekrarları birleştiriyor; dosyanın her yerindeki tekrarları kaldırmak için önce sıralamanın neden gerektiğini buradan anlıyorum. İlk görülme sırası önemliyse sıralamak uygun değil, bu yüzden etiketlerde sırayı koruyarak tekrarları ayıklıyorum. Python tarafında listeyi yerinde sıralamak yerine yeni bir sıralı liste üretmek, talep listesinin özgün sırasını koruyor.

## JavaScript'ten Farklı Çıkan Üç Şey

- Boş listenin doğruluk değeri: Python `bool([])` → `False`; JavaScript `Boolean([])` → `true`, dolayısıyla aynı boş koleksiyonla kurulan koşul farklı davranıyor.
- Sayı ile metnin eşitliği: Python `0 == "0"` → `False`; JavaScript `0 == "0"` → `true`, çünkü JavaScript'in bu karşılaştırması tür dönüşümü yapıyor.
- Sayı ile metnin toplanması: Python `1 + "2"` → `TypeError`; JavaScript `1 + "2"` → `"12"`, bu nedenle Python'da istediğim dönüşümü açıkça seçmem gerekiyor.

## Yanıldığım İki Tahmin

İlk tahminim, standart küçük harf dönüşümünün İ harfini her zaman tek karakterlik i yapacağıydı; birleşen nokta işareti nedeniyle uzunluğun artabilmesi bu beklentiyi bozuyor. İkinci tahminim, bir kümeye dönüştürdüğüm etiketleri ilk gördüğüm sırayla geri alabileceğimdi; sıra garantisi için başka bir yöntem kullanmam gerekiyor.

## En Çok Zorlandığım Konu

En çok zorlandığım konu, bir metin işleminin görünen sonucuyla bütün sınır koşullarını birlikte düşünmek oldu. Türkçe harflerin uzunluğu, boş etiketler ve kısaltmanın kesim noktası için küçük örnekler üzerinden ilerlemek, tek bir başarılı örneğe güvenmekten daha açıklayıcı geliyor.
