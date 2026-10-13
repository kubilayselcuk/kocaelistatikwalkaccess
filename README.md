# Hexagon Erişilebilirlik Analizleri

Bu depo, yaya erişilebilirliği analizlerini gösteren statik bir HTML harita uygulamasıdır.

## Yayına Alma

GitHub Pages ile yayınlamak için:

1. Bu klasörü yeni bir GitHub reposuna yükleyin.
2. GitHub reposunda `Settings > Pages` bölümüne girin.
3. `Build and deployment` altında kaynak olarak `Deploy from a branch` seçin.
4. Branch olarak `main`, klasör olarak `/root` seçip kaydedin.

`index.html` kökte olduğu için ek bir build adımı gerekmez.

## Yerelde Açma

Dosyayı doğrudan tarayıcıda açabilirsiniz:

```text
index.html
```

Harita Leaflet ve Google Fonts CDN bağlantılarını kullandığı için çevrimiçi açıldığında tam görünür.

## Dosyalar

- `index.html`: Yayınlanacak statik harita uygulaması.
- `methodology_hex_access_analysis_en.md`: Analiz metodolojisi dokümanı.
- `build_app.py`: Kaynak GIS verilerinden `index.html` üretmek için kullanılan yardımcı betik.

## Not

Bu GitHub paketi yayın odaklıdır. Geçici klasörler, Python önbellekleri, arşiv dosyaları ve ham çalışma verileri depoya alınmamıştır.
