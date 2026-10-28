# 28.10.2026 Gün Sonu Özeti

Taslak notu: Bu özet mevcut kod ve testlere dayanır; kişisel tahmin ve zorlanma anlatımları kendi deneyimime göre uyarlayabileceğim örneklerdir.

## Sınıf, self ve __init__

Sınıf, aynı tür nesnelerin hangi bilgileri taşıyacağını ve hangi işleri yapacağını bir arada tanımlıyor. `self`, metodu çağıran nesneyi temsil ediyor ve Python'da örnek metotlarının parametrelerinde açıkça yer alıyor. `__init__`, oluşturulmuş nesnenin başlangıç alanlarını hazırlıyor; nesnenin kendisini döndürmek için kullanılmıyor.

## Özel Metotlar: __len__ ve __repr__

`__len__`, nesnemin uzunluğunun ne anlama geldiğini tanımlayarak onu `len` ile kullanılabilir hâle getiriyor. `__repr__` ise hata ayıklarken nesnenin içeriğini anlaşılır biçimde görmemi sağlıyor. Talep modelinde dataclass alanları gösteren bir temsil üretiyor, ancak uzunluk davranışı kendiliğinden eklenmiyor.

## Kalıtım ve super()

Kalıtım sayesinde ortak davranışı üst sınıfta tutup daha özel sınıflarda genişletebiliyorum. `super()`, metot çözümleme sırasındaki sonraki uygulamaya ulaşmamı sağlıyor; böylece başlangıç işlemlerini tekrar yazmadan sürdürebiliyorum. Projede talep hatalarının aynı üst sınıftan türemesi, komutun bu hataları tek bir yerde yakalamasını kolaylaştırıyor.

## dataclass ve frozen

Dataclass, alan tanımlarından başlangıç, karşılaştırma ve temsil metotlarını üreterek tekrar yazmam gereken işleri azaltıyor. `frozen=True`, oluşturulmuş talebin alanlarına yeniden değer atamamı engelliyor ama içerideki değişebilir nesneleri kendiliğinden dondurmuyor. Etiketleri tuple olarak saklamak bu yüzden önemli; alanın tuttuğu koleksiyonu da yerinde değiştiremiyorum.

## Değişebilir Varsayılan Tuzağı

Bir fonksiyon parametresine varsayılan liste koyarsam bu liste her çağrıda yeniden oluşmuyor ve önceki çağrının değişiklikleri sonraki çağrıya taşınabiliyor. Dataclass içinde her nesneye ayrı liste gerektiğinde bir varsayılan üretici kullanmak gerekiyor. Talep modelindeki boş tuple değiştirilemediği için ortak varsayılan olarak güvenle kullanılabiliyor.

## StrEnum

StrEnum, durum ve öncelik gibi sınırlı seçeneklere isim verirken metinlerle çalışmayı da kolaylaştırıyor. Dışarıdan gelen metni enum'a dönüştürürken tanımsız bir değer hata verdiği için yazım yanlışını daha dosya okunurken yakalayabiliyorum. Bu projede enum üyelerinin metinlerle karşılaştırılabilmesi, mevcut filtreleme ve sıralama kurallarının kullanılmasını sağlıyor.

## try, except, else, finally

`try` içine hata beklediğim işlemi, `except` içine ise belirli bir hata oluşursa yapılacak işi koyuyorum. `else`, denenen işlem hata vermeden biterse çalışıyor; `finally` ise normal tamamlanma, hata veya erken dönüş sırasında temizlik yapmamı sağlıyor. Yakalanacak hata türünü dar tutmak, beklenmeyen bir programlama hatasını yanlışlıkla gizlememi önlüyor.

## Kendi Hata Sınıflarım ve raise ... from

Dosyanın okunamaması ile tek bir talebin geçersiz olması farklı sorunlar olduğu için bunları ayrı hata sınıflarıyla anlatabiliyorum. İkisini ortak bir talep hatasının altında toplamak, komutun kullanıcıya mesaj verme işini sadeleştiriyor. `raise ... from`, daha anlaşılır bir hata üretirken asıl nedeni de saklıyor; testlerde bu nedenin doğru hata türü olduğunu kontrol edebiliyorum.

## Talep Modeli: Sınırda Doğrulama

JSON verisini uygulamaya alırken zorunlu alanları ve değerleri denetleyip sözlüğü Talep nesnesine dönüştürüyorum; dosya genelindeki tekrar eden kimlikleri de okuma aşamasında reddediyorum. 8. görevde silinen `test_durum_sayilari_bilinmeyen_durumu_saymaz` testi gereksiz kaldı, çünkü bilinmeyen durum artık bu giriş yolundan sayma fonksiyonuna ulaşmadan hata veriyor. Böylece sayma fonksiyonunda geçersiz durumu sessizce atlamayı sınamak yerine, model testinde bu durumun reddedildiğini doğruluyorum.

## Çıkış Kodu ve Hata Akışı

Başarılı özet standart çıktıya yazılıyor ve komut 0 koduyla tamamlanıyor. Dosya ya da talep hatası tek satırlık mesajla standart hataya yazılıp 1 kodunu üretirken, birden fazla dosya verilmesi kullanım hatası sayılıp 2 kodunu üretiyor. Böylece komutu çağıran başka bir program mesajın metnini çözmeye çalışmadan sonucu çıkış kodundan anlayabiliyor.

## TypeScript'ten Farklı Çıkan Üç Şey

- Nesnenin alanına erişim Python'da `self.baslik`, TypeScript'te `this.baslik` biçiminde yazılıyor; Python'da örnek metodunun parametreleri arasında `self` de açıkça bulunuyor.
- Bir listenin uzunluğunu Python'da `len(etiketler)`, TypeScript'te `etiketler.length` ile alıyorum; Python özel nesnelerde bu işlemi `__len__` üzerinden genişletiyor.
- Hatanın nedenini koruyarak yeni hata üretmek Python'da `raise RuntimeError("okuma başarısız") from hata`, TypeScript'te ES2022 desteğiyle `throw new Error("okuma başarısız", { cause: hata })` biçiminde yazılıyor.

## Yanıldığım İki Tahmin

İlk tahminim, dataclass alanına tip yazmanın dışarıdan gelen yanlış türü otomatik olarak reddedeceğiydi; bunun için ayrıca doğrulama yapmam gerektiğini gördüm. İkinci tahminim, `frozen=True` seçeneğinin içerideki bir listeyi de değiştirilemez yapacağıydı; alan atamasıyla koleksiyonun içeriğini değiştirmenin ayrı işlemler olduğunu ayırt etmem gerekti.

## En Çok Zorlandığım Konu

En çok zorlandığım konu, hangi hatanın modelde üretileceğini ve hangisinin komutta kullanıcıya gösterileceğini ayırmak oldu. Dosya okuma, veri doğrulama ve çıkış kodu adımlarını ayrı düşünmek, aynı denetimi her fonksiyonda tekrarlamamın gerekmediğini anlamamı sağladı. Hatanın ilk nedenini korurken terminalde kısa bir mesaj göstermek de bu ayrımın parçası oldu.
