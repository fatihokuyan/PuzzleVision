🧩 PuzzleVision - Konya Bilim Merkezi İnteraktif Puzzle Sergisi
Konya Bilim Merkezi için özel olarak geliştirilmiş, ziyaretçilerin el hareketleriyle etkileşime girebildiği interaktif bir puzzle (yapboz) deneyimi. Bu proje, bilgisayarlı görü (computer vision) ve el izleme (hand tracking) teknolojilerini kullanarak fiziksel temas gerektirmeyen, yenilikçi ve eğlenceli bir sergi deneyimi sunar.

🚀 Özellikler
Temassız Etkileşim: MediaPipe ve OpenCV kullanılarak geliştirilmiş hassas el izleme teknolojisi sayesinde kullanıcılar, ekran veya fareye dokunmadan sadece el hareketleriyle puzzle parçalarını kontrol edebilir, sürükleyip bırakabilir.

Kullanıcı Dostu Arayüz: PyQt5 ile tasarlanmış, her yaştan ziyaretçiye hitap eden, akıcı ve modern kullanıcı arayüzü.

Zengin Multimedya Desteği: Görseller, animasyonlar, videolar ve ses efektleriyle desteklenen dinamik bir oyun deneyimi.

Modüler ve Sürdürülebilir Yapı: Modüler mimari (grafik, çekirdek iş mantığı, kullanıcı arayüzü ve araçlar) sayesinde kolay yönetilebilir kod tabanı.

🛠️ Kullanılan Teknolojiler
Python: Ana programlama dili.

OpenCV: Kamera entegrasyonu ve gerçek zamanlı görüntü işleme mimarisi.

MediaPipe (Google): Yüksek doğruluklu el (ve parmak) izleme motoru ve iskelet analizi.

PyQt5: Masaüstü grafik kullanıcı arayüzü (GUI) geliştirme.

📁 Proje Yapısı
PuzzleVision/
├── icon_images/       # Arayüzde yer alan yönlendirme ve menü ikonları
├── puzzle_images/     # Ziyaretçilerin tamamlamaya çalıştığı görsel kaynakları
├── puzzle_sounds/     # Doğru/yanlış eşleştirme, tıklama gibi ses efektleri
├── puzzle_videos/     # Arka plan ve yönlendirme videoları (örn: ffplay entegrasyonu)
├── sergi_images/      # Sergide gösterilecek ekstra görseller
├── src/               # Tüm kaynak kodlar (Core mantığı, UI ve algoritmalar)
├── requirements.txt   # Projenin çalışması için gereken Python kütüphaneleri listesi
└── run.py             # Uygulamayı başlatan ve sistemi ayağa kaldıran ana dosya
⚙️ Kurulum ve Çalıştırma
Projeyi kendi ortamınızda test etmek veya çalıştırmak için aşağıdaki adımları sırasıyla uygulayabilirsiniz:

Depoyu Klonlayın:

Bash
git clone https://github.com/fatihokuyan/PuzzleVision.git
cd PuzzleVision
Sanal Ortam (Virtual Environment) Oluşturun (Önerilir):

Bash
python -m venv venv

# Windows için Aktifleştirme:
venv\Scripts\activate

# MacOS veya Linux için Aktifleştirme:
source venv/bin/activate
Gerekli Kütüphaneleri Yükleyin:

Bash
pip install -r requirements.txt
Uygulamayı Başlatın:
Kameranızın bağlı olduğundan emin olduktan sonra projeyi çalıştırın:

Bash
python run.py
🎯 Serginin Amacı ve Detaylar
Bu proje, Konya Bilim Merkezi'ne gelen başta çocuklar ve gençler olmak üzere tüm ziyaretçiler için tasarlanmıştır. Amacı; hem ziyaretçilerin motor becerilerini ve problem çözme yeteneklerini geliştiren geleneksel "puzzle" kavramını korumak, hem de yeni nesil yapay zeka ve görüntü işleme teknolojilerini deneyimlemelerini sağlamaktır.

Kameradan alınan anlık görüntüler işlenerek kullanıcının el koordinatları milisaniyeler içerisinde tespit edilir. Ziyaretçi ekrandaki bir yapboz parçasının üzerine elini getirdiğinde ve parmaklarıyla yakalama (kavrama) hareketi yaptığında sanal olarak parçayı tutmuş olur.

🤝 Geliştirme ve İletişim
Bu yazılım özel bir interaktif sergi ürünü olarak tasarlanmıştır. Herhangi bir sorunuz, öneriniz veya olası hata bildirimleriniz için deponun [Issues] sekmesini kullanabilirsiniz.

Not: Proje içindeki eğitim videoları dosya boyutu nedeniyle depoya dahil edilmemiştir.

💻 Geliştirici: Fatih Okuyan
🏢 Kurum: Konya Bilim Merkezi (İnteraktif Sergiler)
🔖 Lisans: Bu projenin kullanım hakları tamamen ilgili kuruma / geliştiriciye aittir. İzinsiz kopyalanması veya ticari amaçla kullanılması yasaktır.

🧩 PuzzleVision - Konya Science Center Interactive Puzzle Exhibition
An interactive puzzle experience specially developed for the Konya Science Center, where visitors can interact using hand gestures. This project offers an innovative and fun exhibition experience that requires no physical contact, utilizing computer vision and hand tracking technologies.

🚀 Features
Touchless Interaction: Using hand tracking technology developed with MediaPipe and OpenCV, users can control, drag, and drop puzzle pieces using only hand movements without touching a screen or mouse.

User-Friendly Interface: A fluid and modern UI designed with PyQt5, appealing to visitors of all ages.

Rich Multimedia Support: A dynamic gaming experience supported by images, animations, videos, and sound effects.

Modular and Sustainable Structure: An easily manageable codebase thanks to modular architecture (graphics, core logic, UI, and tools).

🛠️ Technologies Used
Python: Main programming language.

OpenCV: Camera integration and real-time image processing architecture.

MediaPipe (Google): High-accuracy hand/finger tracking engine and skeletal analysis.

PyQt5: Desktop graphical user interface (GUI) development.

📁 Project Structure
PuzzleVision/
├── icon_images/       # UI icons and navigation graphics
├── puzzle_images/     # Visual assets for the puzzles
├── puzzle_sounds/     # Sound effects for matching, clicks, etc.
├── puzzle_videos/     # Background and guidance videos (e.g., ffplay integration)
├── sergi_images/      # Additional exhibition visuals
├── src/               # Source code (Core logic, UI, and algorithms)
├── requirements.txt   # List of required Python libraries
└── run.py             # Main entry point to launch the application
⚙️ Installation and Execution
To test or run the project in your local environment, follow these steps:

Clone the Repository:

Bash
git clone https://github.com/fatihokuyan/PuzzleVision.git
cd PuzzleVision
Create a Virtual Environment (Recommended):

Bash
python -m venv venv

# For Windows:
venv\Scripts\activate

# For MacOS or Linux:
source venv/bin/activate
Install Dependencies:

Bash
pip install -r requirements.txt
Run the Application:
Ensure your camera is connected and run:

Bash
python run.py
🎯 Purpose and Details
This project is designed for all visitors of the Konya Science Center, primarily children and young adults. It aims to preserve the traditional "puzzle" concept that develops motor skills and problem-solving abilities while allowing visitors to experience next-generation AI and image processing technologies.

Real-time images from the camera are processed to detect hand coordinates within milliseconds. When a visitor places their hand over a puzzle piece on the screen and makes a "grabbing" gesture, they virtually hold the piece.

🤝 Development and Contact
This software is designed as a custom interactive exhibition product. For any questions, suggestions, or bug reports, please use the [Issues] tab of the repository.

Note: Educational videos within the project are not included in the repository due to file size constraints.

💻 Developer: Fatih Okuyan
🏢 Organization: Konya Science Center (Interactive Exhibitions)
🔖 License: All rights to this project belong to the respective organization/developer. Unauthorized copying or commercial use is prohibited.
