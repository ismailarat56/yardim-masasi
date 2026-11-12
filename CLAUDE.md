# Claude için çalışma kuralları

## Kurallar

- İzin almadan commit veya push yapma. Her commit ve push öncesinde açıkça sor.
- README'ye birebir uy. Kurulum ve çalıştırma adımlarında README'deki komutları kullan, kendi kestirme yolunu icat etme.

## İki bilgisayarda çalışma

Proje hem bir Linux bilgisayarda hem de Windows'taki WSL Ubuntu'da (`~/yardim-masasi`) geliştiriliyor. İki makine GitHub üzerinden eşitleniyor.

- İşe başlarken `git pull` çalıştır.
- Makineden kalkmadan önce yapılan işi commit'le ve push et (önce izin iste).
- `.env` ve `.env.db` Git'e girmez; her makinede `.env.example` ve `.env.db.example` dosyalarından kopyalanır.
- Veritabanı her makinede ayrı bir Docker biriminde (`db-data`) durur ve Git ile taşınmaz. Veri taşımak gerekirse `pg_dump` kullanılır.
