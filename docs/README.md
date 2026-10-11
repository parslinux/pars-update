# Pars Update (pars-update)

**Pars Update**, Debian tabanlı işletim sistemleri ve Pars Linux için geliştirilmiş, hafif, güvenli ve modern bir grafiksel güncelleme yöneticisidir.

---

## 🌟 Temel Özellikler

* **Modern ve Sade Arayüz:** GTK+ 3 ve VTE terminal entegrasyonu ile canlı güncelleme çıktıları.
* **Sistem Tepsisi (Tray) Bildirimi:** Ayatana AppIndicator ile sistem durumunu ve bekleyen güncelleme sayısını arka plandan takip etme.
* **Güvenli Çevrimdışı Güncelleme:** Systemd `system-update.target` ve Plymouth açılış ekranı üzerinden oturumu riske atmadan güvenli yükseltme.
* **Yetki Ayrımı (Polkit):** GUI süreci yetkisiz çalışırken, paket işlemleri Polkit üzerinden güvenli şekilde yürütülür.
* **Parolasız Güncelleme:** İsteğe bağlı `pars-update` grubu ile her güncellemede parola girmeden işlem yapabilme.
* **Önbellek & Artık Paket Temizliği:** İndirilen `.deb` paketlerini, kullanılmayan bağımlılıkları ve artık yapılandırma dosyalarını tek tıkla temizleme.
* **Kaynak Listesi Onarımı:** Bozuk `sources.list` girdilerini otomatik tespit edip varsayılanlara döndürme.
* **Seçilebilir Güncellemeler:** Kullanıcının yalnızca istediği paketleri seçerek güncelleyebilmesi.

---

## 📸 Ekran Görüntüleri

| Ana Güncelleme Ekranı | Paket Seçimi ve Detaylar |
| :---: | :---: |
| ![Pars Update 1](../screenshots/pardus-update-1.png) | ![Pars Update 2](../screenshots/pardus-update-2.png) |

---

## 🚀 Hızlı Başlangıç

### Bağımlılıkları Yükleme
```bash
sudo apt update
sudo apt install -y python3 python3-apt python3-distro gir1.2-glib-2.0 \
    gir1.2-gtk-3.0 gir1.2-notify-0.7 gir1.2-soup-2.4 gir1.2-vte-2.91 \
    gir1.2-ayatanaappindicator3-0.1 policykit-1 gettext
```

### Kaynaktan Çalıştırma
```bash
python3 src/Main.py
```

### Debian (.deb) Paketi Derleme
```bash
sudo apt install -y devscripts git-buildpackage
sudo mk-build-deps -ir
gbp buildpackage --git-export-dir=/tmp/build/pars-update -us -uc
```

---

## 📚 Dokümantasyon Rehberi (Docs Index)

Projenin tüm teknik, operasyonel ve kullanıcı dokümanlarına aşağıdaki bağlantılardan ulaşabilirsiniz:

### Çekirdek ve Sistem Dokümantasyonu
* 🏗️ **[Sistem Mimarisi (ARCHITECTURE.md)](ARCHITECTURE.md)**: Çift katmanlı süreç mimarisi, Polkit ve IPC entegrasyonu.
* 📦 **[Kurulum Kılavuzu (INSTALL.md)](INSTALL.md)**: Ayrıntılı derleme, bağımlılıklar ve kurulum adımları.
* 🛡️ **[Güvenlik Politikası (SECURITY.md)](SECURITY.md)**: Yetki ayrımı, girdi doğrulama ve güvenlik açığı bildirim süreci.
* 💻 **[Komut Satırı Referansı (CLI_REFERENCE.md)](CLI_REFERENCE.md)**: `pars-update` ve arka plan betiklerinin tüm parametreleri.

### Entegrasyon ve Yönetim Kılavuzları
* 🔗 **[Uygulama ve Masaüstü Entegrasyonu (UYGULAMA_BAGLAMA.md)](UYGULAMA_BAGLAMA.md)**: Desktop dosyaları, otomatik başlatma ve harici çağırma.
* 🌐 **[Özel Depo ve Sunucu Barındırma (SELF_HOSTING_GUIDE.md)](SELF_HOSTING_GUIDE.md)**: Kurumsal APT deposu ve `dists.json` sürüm uç noktası kurulumu.
* 💾 **[Veri ve Kota Tasarrufu (DATA_SAVING_GUIDE.md)](DATA_SAVING_GUIDE.md)**: Disk alanı ve mobil internet kotası tasarruf yöntemleri.

### Geliştirme ve Topluluk
* 🤝 **[Katkı Sağlama Rehberi (CONTRIBUTING.md)](CONTRIBUTING.md)**: PR iş akışı, kod standartları ve kurallar.
* 🧪 **[Test ve Kalite Güvencesi (TESTING.md)](TESTING.md)**: Birim, arayüz ve paket derleme testleri.
* 🌍 **[Çeviri Kılavuzu (TRANSLATION_GUIDE.md)](TRANSLATION_GUIDE.md)**: GNU gettext ile yeni dil ekleme ve güncelleme.
* 🤖 **[AI & Asistan Yönergesi (CLAUDE.md)](CLAUDE.md)**: AI ajanları ve geliştiriciler için mimari standartlar.
* 📈 **[İlerleme ve Yol Haritası (progress.md)](progress.md)**: Tamamlanan ve planlanan özellikler.
* 🏷️ **[Sürüm Yönetimi (VERSION.md)](VERSION.md)**: SemVer sürümleme politikası ve yayınlama adımları.
* 📜 **[Değişiklik Günlüğü (CHANGELOG.md)](CHANGELOG.md)**: Sürümler arası detaylı değişiklik listesi.

### Hukuki ve Finansal Prensipler
* ⚖️ **[Kullanım Şartları ve Garanti Reddi (TERMS.md / SARTLAR.md)](TERMS.md)**: GPLv3 lisanslama ve sorumluluk sınırları.
* 💳 **[Finansman ve Bağış Modeli (PAYMENT_INTEGRATION.md)](PAYMENT_INTEGRATION.md)**: Ticari olmayan açık kaynak yapısı ve bağış kanalları.

---

## 📄 Lisans
Bu proje [GNU Genel Kamu Lisansı Sürüm 3 (GPLv3)](../LICENSE) altında lisanslanmıştır.
