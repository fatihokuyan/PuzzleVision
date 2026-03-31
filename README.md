# 🧩 PuzzleVision - Konya Bilim Merkezi İnteraktif Puzzle Sergisi

Konya Bilim Merkezi için özel olarak geliştirilmiş, ziyaretçilerin el hareketleriyle etkileşime girebildiği interaktif bir puzzle (yapboz) deneyimi. Bu proje, bilgisayarlı görü (computer vision) ve el izleme (hand tracking) teknolojilerini kullanarak fiziksel temas gerektirmeyen, yenilikçi ve eğlenceli bir sergi deneyimi sunar.

## 🚀 Özellikler

- **Temassız Etkileşim:** MediaPipe ve OpenCV kullanılarak geliştirilmiş hassas el izleme teknolojisi sayesinde kullanıcılar, ekran veya fareye dokunmadan sadece el hareketleriyle puzzle parçalarını kontrol edebilir, sürükleyip bırakabilir.
- **Kullanıcı Dostu Arayüz:** PyQt5 ile tasarlanmış, her yaştan ziyaretçiye hitap eden, akıcı ve modern kullanıcı arayüzü.
- **Zengin Multimedya Desteği:** Görseller, animasyonlar, videolar ve ses efektleriyle desteklenen dinamik bir oyun deneyimi.
- **Modüler ve Sürdürülebilir Yapı:** Modüler mimari (grafik, çekirdek iş mantığı, kullanıcı arayüzü ve araçlar) sayesinde kolay yönetilebilir kod tabanı.

## 🛠️ Kullanılan Teknolojiler

- **[Python](https://www.python.org/):** Ana programlama dili.
- **[OpenCV](https://opencv.org/):** Kamera entegrasyonu ve gerçek zamanlı görüntü işleme mimarisi.
- **[MediaPipe (Google)](https://developers.google.com/mediapipe):** Yüksek doğruluklu el (ve parmak) izleme motoru ve iskelet analizi.
- **[PyQt5](https://riverbankcomputing.com/software/pyqt/intro):** Masaüstü grafik kullanıcı arayüzü (GUI) geliştirme.

## 📁 Proje Yapısı

```
PuzzleVision/
├── icon_images/       # Arayüzde yer alan yönlendirme ve menü ikonları
├── puzzle_images/     # Ziyaretçilerin tamamlamaya çalıştığı görsel kaynakları
├── puzzle_sounds/     # Doğru/yanlış eşleştirme, tıklama gibi ses efektleri
├── puzzle_videos/     # Arka plan ve yönlendirme videoları (örn: ffplay entegrasyonu)
├── sergi_images/      # Sergide gösterilecek ekstra görseller
├── src/               # Tüm kaynak kodlar (Core mantığı, UI ve algoritmalar)
├── requirements.txt   # Projenin çalışması için gereken Python kütüphaneleri listesi
└── run.py             # Uygulamayı başlatan ve sistemi ayağa kaldıran ana dosya
```

## ⚙️ Kurulum ve Çalıştırma

Projeyi kendi ortamınızda test etmek veya çalıştırmak için aşağıdaki adımları sırasıyla uygulayabilirsiniz:

1. **Depoyu Klonlayın:**
   ```bash
   git clone https://github.com/kullaniciadiniz/PuzzleVision.git
   cd PuzzleVision
   ```

2. **Daha İzole Bir Ortam İçin Sanal Ortam (Virtual Environment) Oluşturun (Önerilir):**
   ```bash
   python -m venv venv
   
   # Windows için Aktifleştirme:
   venv\Scripts\activate
   
   # MacOS veya Linux için Aktifleştirme:
   source venv/bin/activate
   ```

3. **Gerekli Kütüphaneleri Yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Uygulamayı Başlatın:**
   Kameranızın bağlı olduğundan emin olduktan sonra projeyi çalıştırın:
   ```bash
   python run.py
   ```

## 🎯 Serginin Amacı ve Detaylar

Bu proje, **Konya Bilim Merkezi**'ne gelen başta çocuklar ve gençler olmak üzere tüm ziyaretçiler için tasarlanmıştır. Amacı; hem ziyaretçilerin motor becerilerini ve problem çözme yeteneklerini geliştiren geleneksel "puzzle" kavramını korumak, hem de yeni nesil yapay zeka ve görüntü işleme teknolojilerini deneyimlemelerini sağlamaktır.

Kameradan alınan anlık görüntüler işlenerek kullanıcının el koordinatları milisaniyeler içerisinde tespit edilir. Ziyaretçi ekrandaki bir yapboz parçasının üzerine elini getirdiğinde ve parmaklarıyla yakalama (kavrama) hareketi yaptığında sanal olarak parçayı tutmuş olur.

## 🤝 Geliştirme ve İletişim

Bu yazılım özel bir interaktif sergi ürünü olarak tasarlanmıştır. Herhangi bir sorunuz, öneriniz veya olası hata bildirimleriniz için deponun **[Issues]** sekmesini kullanabilirsiniz.

---

"Not: Proje içindeki eğitim videoları dosya boyutu nedeniyle depoya dahil edilmemiştir.

💻 **Geliştirici:** fatih
🏢 **Kurum:** Konya Bilim Merkezi (İnteraktif Sergiler)
🔖 **Lisans:** Bu projenin kullanım hakları tamamen ilgili kuruma / geliştiriciye aittir. İzinsiz kopyalanması veya ticari amaçla kullanılması yasaktır. 
