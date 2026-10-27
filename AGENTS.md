# Proje Çalışma Yönergeleri

## Commit ve Push

Kullanıcının 27.10.2026 tarihli kalıcı çalışma tercihi:

- Tamamlanan her anlamlı proje değişikliğini ayrı bir commit olarak kaydet. Birbirinden bağımsız işleri tek committe birleştirme.
- Her committen sonra ilgili dalı GitHub'daki `origin` remote'una ayrı bir push ile gönder. Kullanıcı bu akış için yetki verdi; her seferinde yeniden onay isteme. Ortamın zorunlu izin kontrolleri geçerlidir.
- Commit öncesinde değişiklikleri incele ve uygun kontrolleri çalıştır. Python kodu veya bağımlılık değişikliklerinde `uv run --locked pytest -q` kullan.
- Yalnız ilgili dosyaları stage et; `.env`, `.venv`, geçici çıktılar ve görevle ilgisiz yerel değişiklikleri commitlere dahil etme.
- Kullanıcı ayrıca istemedikçe geçmişi yeniden yazma ve force push yapma. Push başarısız olursa bunu açıkça bildir; gönderilmemiş işi gönderilmiş gibi sunma.
- Sonuç mesajında yapılan işi, doğrulama sonucunu ve commit/push durumunu kısaca belirt.
