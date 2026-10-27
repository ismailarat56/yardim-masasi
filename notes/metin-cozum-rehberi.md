# Metin İşleme Görevi: Çözüm ve Açıklamalar

Bu belge, verilen altı fonksiyonun tamamlanmış çözümünü ve testleri kendi terminalinde nasıl çalıştıracağını anlatır. Kodlar yalnızca bu Markdown dosyasında yer alır; `src/yardim_masasi/metin.py` ve `tests/test_metin.py` bu çalışma kapsamında oluşturulmadı, test çalıştırılmadı.

## 1. Kodun Tamamlanmış Hali

Aşağıdaki kod, görevi uygulamaya karar verdiğinde `src/yardim_masasi/metin.py` dosyasına yazacağın içeriktir. Ek bir paket veya içe aktarma gerektirmez.

```python
def kucuk_harf(metin: str) -> str:
    return metin.replace("İ", "i").replace("I", "ı").lower()


def buyuk_harf(metin: str) -> str:
    return metin.replace("i", "İ").replace("ı", "I").upper()


def bosluklari_duzelt(metin: str) -> str:
    return " ".join(metin.split())


def etiketleri_ayir(metin: str) -> list[str]:
    etiketler = [
        kucuk_harf(bosluklari_duzelt(parca))
        for parca in metin.split(",")
    ]
    dolu_etiketler = [etiket for etiket in etiketler if etiket]
    return list(dict.fromkeys(dolu_etiketler))


def kisalt(metin: str, en_fazla: int = 30) -> str:
    if len(metin) <= en_fazla:
        return metin
    return metin[:en_fazla - 1].rstrip() + "…"


def maskele(eposta: str) -> str:
    ad, ayrac, alan = eposta.partition("@")
    if not ayrac or not ad or not alan:
        return "***"
    return f"{ad[0]}***@{alan}"
```

## 2. Fonksiyon İmzalarını Okumak

Şu satırı parçalara ayıralım:

```python
def kisalt(metin: str, en_fazla: int = 30) -> str:
```

| Parça | Anlamı |
| --- | --- |
| `def` | Bir fonksiyon tanımlar. |
| `kisalt` | Fonksiyonun adıdır. |
| `metin` | İşlenecek metnin parametresidir. |
| `: str` | Bu parametre için metin beklendiğini belirten tip ipucudur. |
| `en_fazla: int` | İzin verilen uzunluğun tam sayı olmasının beklendiğini belirtir. |
| `= 30` | İkinci argüman verilmezse kullanılacak varsayılan değerdir. |
| `-> str` | Fonksiyonun bir metin döndürmesinin beklendiğini belirtir. |
| Sondaki `:` | Girintili fonksiyon gövdesini başlatır. |

**Parametre**, fonksiyon tanımındaki isimdir; **argüman**, çağrıda verdiğin değerdir. `kisalt("Fatura gelmedi", 8)` çağrısında `"Fatura gelmedi"` ve `8` argümanlardır; içeride bunlara `metin` ve `en_fazla` isimleriyle erişilir.

```python
kisalt("Fatura gelmedi")                # en_fazla = 30
kisalt("Fatura gelmedi", 8)             # en_fazla = 8
kisalt("Fatura gelmedi", en_fazla=8)    # Aynı değer, adıyla verildi.
```

Tip ipuçları açıklama ve araç desteği sağlar; Python bu ipuçları nedeniyle kendiliğinden tür kontrolü veya tür dönüşümü yapmaz. `-> list[str]`, dönüş değerinin metinlerden oluşan bir liste olmasının beklendiğini söyler.

`return`, sonucu çağıran yere verir ve fonksiyonu bitirir. `print`, terminale yazar. Testler dönüş değerlerini karşılaştırdığı için bu fonksiyonlarda sonuçlar `return` ile verilmelidir.

## 3. Küçük Harfe Çevirme

```python
return metin.replace("İ", "i").replace("I", "ı").lower()
```

Metotlar soldan sağa uygulanır:

1. `replace("İ", "i")`, büyük noktalı İ harflerinin tamamını küçük noktalı i yapar.
2. `replace("I", "ı")`, büyük noktasız I harflerinin tamamını küçük noktasız ı yapar.
3. `lower()`, diğer harfleri küçültür.

`replace(eski, yeni)` iki argüman alır. Burada adet sınırı verilmediği için eşleşen bütün parçaları değiştirir. Metinler değiştirilemez olduğundan her adım yeni bir metin döndürür; sonraki metot o sonuç üzerinde çalışır.

Python'ın standart `lower()` işlemi Türkçeye özel değildir. `"İ".lower()` sonucu `i` ve birleşen nokta işaretinden oluşur; `len()` bunu iki Unicode kod noktası olarak sayar. Önce `İ` harfini doğrudan `i` yapınca bu sorun oluşmaz.

```text
İSTANBUL → iSTANBUL → iSTANBUL → istanbul
IŞIK     → IŞIK     → ıŞıK     → ışık
İsmail   → ismail; uzunluk 6
```

## 4. Büyük Harfe Çevirme

```python
return metin.replace("i", "İ").replace("ı", "I").upper()
```

Bu kez küçük i, büyük noktalı İ'ye; küçük ı, büyük noktasız I'ya çevrilir. Kalan harflere `upper()` uygulanır.

Önce `upper()` uygulansaydı `i` harfi `I` olurdu ve başlangıçta noktalı mı noktasız mı olduğu bilgisi kaybolurdu. Bu nedenle Türkçe harfler önce ele alınır.

```text
istanbul → İstanbul → İstanbul → İSTANBUL
ılık su  → ılık su  → IlIk su  → ILIK SU
```

## 5. Boşlukları Düzeltme

```python
return " ".join(metin.split())
```

Argümansız `split()`, metni boşluk karakteri gruplarından böler. Sekme (`\t`) ve satır sonu (`\n`) da buna dahildir. Baştaki ve sondaki boşluklar boş liste elemanları oluşturmaz.

```python
"  Giriş \t yapamıyorum\n ".split()
# ["Giriş", "yapamıyorum"]
```

`" ".join(...)`, parçaları aralarına tek boşluk koyarak birleştirir. Metodun solundaki `" "`, birleştirme sırasında kullanılacak ayırıcıdır.

```python
" ".join(["Giriş", "yapamıyorum"])
# "Giriş yapamıyorum"
```

Yalnızca boşluk içeren metnin `split()` sonucu `[]` olur. Boş listenin `join()` sonucu da `""` olur.

Burada `split(" ")` kullanmıyoruz: açıkça tek boşlukla bölmek, argümansız `split()` ile aynı davranış değildir; sekme ve satır sonlarını aynı şekilde işlemez.

## 6. Etiketleri Ayırma

İlk işlem virgüllerden bölmek ve her parçayı temizlemektir:

```python
etiketler = [
    kucuk_harf(bosluklari_duzelt(parca))
    for parca in metin.split(",")
]
```

Bu yapı bir **list comprehension**, yani listeyi döngüyle kısa yoldan oluşturma ifadesidir. Aynı işlemin uzun hali şöyledir:

```python
etiketler = []
for parca in metin.split(","):
    temiz = bosluklari_duzelt(parca)
    kucuk = kucuk_harf(temiz)
    etiketler.append(kucuk)
```

İç içe fonksiyon çağrısında önce içteki çağrı çalışır: `bosluklari_duzelt(parca)` sonucuna `kucuk_harf` uygulanır.

Örnek girdinin ilk aşamadaki sonucu:

```text
Girdi: "Hesap, GİRİŞ ,, hesap , Ödeme   Sorunu"
Liste: ["hesap", "giriş", "", "hesap", "ödeme sorunu"]
```

Ardından boş metinler atılır:

```python
dolu_etiketler = [etiket for etiket in etiketler if etiket]
```

`if etiket`, metnin boş olup olmadığını kontrol eder. Boş metin koşulda yanlış, boş olmayan metin doğru kabul edilir.

Son adım tekrarları kaldırır:

```python
return list(dict.fromkeys(dolu_etiketler))
```

`dict.fromkeys`, elemanları sözlük anahtarı yapar; değerleri varsayılan olarak `None` olur. Sözlükte aynı anahtar ikinci kez bulunamaz ve Python sözlükleri eklenme sırasını korur. `list(...)` sözlüğün anahtarlarını sırayla listeye dönüştürür.

```text
["hesap", "giriş", "hesap", "ödeme sorunu"]
→ {"hesap": None, "giriş": None, "ödeme sorunu": None}
→ ["hesap", "giriş", "ödeme sorunu"]
```

Doğrudan `list(set(...))` kullanmak ilk görülme sırasını garanti etmez. Burada sözlük, hem tekrarları kaldırmak hem sırayı korumak için kullanılır.

## 7. Metni Kısaltma

```python
if len(metin) <= en_fazla:
    return metin
return metin[:en_fazla - 1].rstrip() + "…"
```

`len(metin)` uzunluğu verir. Metin sınıra eşitse veya daha kısaysa doğrudan döner; boşluklarına bile dokunulmaz.

Uzun metinde `metin[:en_fazla - 1]` dilimi alınır. `[:n]`, başlangıçtan `n` konumuna kadar olan parçadır; `n` konumundaki karakter dahil değildir. Üç nokta işareti için bir karakterlik yer ayrılır.

`rstrip()`, kesilen parçanın yalnızca sağındaki boşluk karakterlerini kaldırır. Böylece kesim bir boşluğa denk geldiğinde `"Fatura …"` yerine `"Fatura…"` elde edilir.

```text
metin = "Fatura gelmedi", en_fazla = 8
İlk 7 karakter: "Fatura "
rstrip sonrası: "Fatura"
İşaret eklenince: "Fatura…"
```

Sonuç sınırı doldurmak zorunda değildir; sınırı aşmaması yeterlidir. `"…"` tek karakterdir ve `"\u2026"` ile aynı metindir. Üç ayrı noktadan oluşan `"..."` ise üç karakterdir ve bu sözleşmede kullanılmaz.

`en_fazla=1` için uzun metnin dilimi `metin[:0]`, yani boş metindir; sonuç yalnız `"…"` olur. Sözleşmeye göre 1'den küçük sınırlar verilmediği için ek kontrol eklenmedi.

## 8. E-posta Maskeleme

```python
ad, ayrac, alan = eposta.partition("@")
```

`partition("@")`, ilk `@` işaretine göre her zaman üç parçalı bir tuple döndürür. Soldaki üç isme bu parçaları dağıtmaya **unpacking**, yani açma denir.

| Girdi | `ad` | `ayrac` | `alan` |
| --- | --- | --- | --- |
| `ayse@example.com` | `ayse` | `@` | `example.com` |
| `gecersiz` | `gecersiz` | `""` | `""` |
| `@example.com` | `""` | `@` | `example.com` |
| `ayse@` | `ayse` | `@` | `""` |

Geçersiz durumların kontrolü:

```python
if not ayrac or not ad or not alan:
    return "***"
```

`not`, koşulun doğruluk değerini tersine çevirir; örneğin `not ""` doğrudur. `or`, koşullardan herhangi biri doğruysa bütün koşulu doğru yapar. Yani ayırıcı, ad veya alan boşsa yalnızca `***` döndürülür.

Geçerli durumda:

```python
return f"{ad[0]}***@{alan}"
```

`ad[0]` ilk karakterdir; Python'da indeksler sıfırdan başlar. Başındaki `f`, metnin bir **f-string** olduğunu belirtir; süslü parantezlerin içindeki ifadelerin değerleri metne yerleştirilir.

Adın boş olmadığını önce kontrol ettiğimiz için `ad[0]` boş metinde çalıştırılmaz. Ad tek harf de olsa üç yıldız eklenir: yıldız sayısı adın uzunluğundan hesaplanmaz. Bu çözüm, sözleşmede belirtilen biçim kontrollerini yapar; kapsamlı e-posta doğrulaması yapmaz.

## 9. Testleri Sen Nasıl Çalıştıracaksın?

Bu bölümdeki komutlar uygulama talimatıdır; bu belge hazırlanırken çalıştırılmadı. Aşağıdaki başarı çıktısı da beklenen sonuç örneğidir, alınmış bir test sonucu değildir.

### Dosyaları Hazırlama

1. Editörde `src/yardim_masasi/metin.py` dosyasını oluştur ve ilk bölümdeki tamamlanmış kodu içine koy. Markdown'daki üç ters tırnaklı kod bloğu sınırlarını kopyalama.
2. Editörde `tests/test_metin.py` dosyasını oluştur ve görevde sana verilen 13 testin tamamını değiştirmeden yapıştır. Testler çözümüne uysun diye beklenen değerleri değiştirme.
3. İki dosyayı da kaydet. Terminalde projenin kök dizininde, yani `pyproject.toml` dosyasının bulunduğu dizinde olduğundan emin ol.

İstersen önce verilen `raise NotImplementedError(...)` gövdeli iskeleti kaydedip testleri çalıştırarak başlangıçtaki 13 başarısızlığı görebilir, sonra gövdeleri çözümle değiştirebilirsin. Bu aşama, testlerin henüz yazılmamış fonksiyonları yakaladığını görmeyi sağlar.

### On Üç Testi Çalıştırma

```bash
uv run pytest -q tests/test_metin.py
```

| Komut parçası | Görevi |
| --- | --- |
| `uv run` | Komutu projenin Python ortamında çalıştırır. |
| `pytest` | Test dosyalarını ve `test_` ile başlayan test fonksiyonlarını çalıştırır. |
| `-q` | Daha kısa çıktı verir. |
| `tests/test_metin.py` | Yalnızca bu dosyadaki testleri seçer. |

Projedeki kilit dosyasının değişmesini engellemek için aynı komutu şöyle de yazabilirsin:

```bash
uv run --locked pytest -q tests/test_metin.py
```

`--locked`, uv'ye verilen seçenektir; bu yüzden `pytest` sözcüğünden önce yer alır. Kilit dosyası proje tanımıyla uyumsuzsa komut hata verir.

Görevin hedefi 13 testin tamamının geçmesidir. Başarı durumundaki çıktı şu biçimde olur; süre makineye göre değişir:

```text
.............                                                            [100%]
13 passed in ...s
```

### Yalnızca Kısaltma Testlerini Çalıştırma

```bash
uv run pytest -q tests/test_metin.py -k kisalt
```

`-k kisalt`, adında `kisalt` geçen testleri seçer. Verilen dosyada bunlar dört testtir. Diğer testlerin `deselected` olarak görünmesi başarısızlık değildir; seçilmedikleri anlamına gelir. Bu dört test geçse bile görev bitmez: sonunda dosyanın tamamını çalıştırmalısın.

Tek bir testi de tam adıyla seçebilirsin:

```bash
uv run pytest -q tests/test_metin.py::test_kisalt_kesilen_yerdeki_boslugu_atar
```

### Başarısız Test Çıktısını Okuma

Bir `assert`, ifadenin doğru olmasını bekler:

```python
assert maskele("ayse@example.com") == "a***@example.com"
```

Solda fonksiyonun ürettiği değer, sağda beklenen değer bulunur. Eşleşmezlerse test başarısız olur. Bir test fonksiyonunda ilk başarısız `assert`, o fonksiyonun kalanını durdurur; pytest varsayılan olarak diğer testleri çalıştırmaya devam eder. Bu yüzden test sayısı, toplam `assert` sayısı değildir.

| Çıktı | Bakılacak yer |
| --- | --- |
| `NotImplementedError` | İlgili gövdede iskeletten kalan `raise` satırı var mı? |
| `AssertionError` | Dönen değer ile beklenen değer nerede farklı? |
| `IndentationError` | Kodun girintileri doğru mu? Gövdelerde dört boşluk kullan. |
| `ModuleNotFoundError` | Dosya yolu doğru mu, dosya kaydedildi mi, komut proje kökünden `uv run` ile mi çalıştırılıyor? |

Örneğin kısaltma testi kırılırsa önce sınırdan bir karakter ayırıp ayırmadığını, tek karakterlik `…` kullandığını ve `rstrip()` işlemini dilimden sonra uyguladığını kontrol et. Etiket testi kırılırsa temizleme, küçültme, boşları atma ve tekrarları kaldırma sırasına bak.

Verilen 13 testin dağılımı: küçük harf için 2, büyük harf için 1, boşluk düzeltme için 1, etiket ayırma için 3, kısaltma için 4, maskeleme için 2 test. Hepsi geçtiğinde görevin belirtilen sözleşmesi sağlanmış olur.
