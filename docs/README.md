# Pars Update (pars-update)

**Pars Update**, Pars Linux, Arch Linux ve Debian tabanlı işletim sistemleri için geliştirilmiş, çoklu paket yöneticisi (Pacman & APT) destekli, hafif, güvenli ve modern bir grafiksel güncelleme yöneticisidir.

---

## 🌟 Temel Özellikler

* **Modern Libadwaita & GTK4 Arayüzü:** GNOME HIG standartlarında akıcı, zarif ve modern arayüz (`Adw.ApplicationWindow`, `Adw.PreferencesWindow`, `Adw.ToastOverlay`).
* **Çekirdek & Arayüz Ayrımı (Decoupled Core):** İş mantığı ve paket yönetim fonksiyonları bağımsız `src/core` katmanında yürütülür; arayüzden bağımsız test edilebilir.
* **Geriye Dönük Uyumluluk (GTK3 Fallback):** Eski sistemler ve özel tercihler için `--gtk3` parametresiyle klasik arayüz desteği korunur.
* **Çift Paket Yöneticisi Desteği:** Arch Linux (`pacman`, `checkupdates`) ve Debian (`apt`) sistemlerini otomatik algılayıp yerel araçlarıyla en yüksek hızda çalışma.
* **Toplu Sorgulama Performansı:** Arch Linux'ta tek `pacman -Si` çağrısıyla tüm paket boyut ve bilgileri anında hesaplanır.
* **VTE Terminal Entegrasyonu:** Güncelleme işlemleri sırasında terminal çıktılarını canlı ve renkli olarak kullanıcıya sunar.
* **Sistem Tepsisi & Bildirimler:** Yeni güncellemeler ve tamamlanan işlemler için masaüstü bildirimleri (`Notify`).
* **Güvenli Çevrimdışı Güncelleme:** Systemd `system-update.target` ve Plymouth açılış ekranı üzerinden oturumu riske atmadan güvenli yükseltme.
* **Yetki Ayrımı (Polkit):** GUI süreci yetkisiz çalışırken, paket işlemleri Polkit üzerinden güvenli şekilde yürütülür.
* **Parolasız Güncelleme:** İsteğe bağlı `pars-update` grubu ile her güncellemede parola girmeden işlem yapabilme.
* **Önbellek & Artık Paket Temizliği:** İndirilen paket arşivlerini (`pacman -Sc` / `apt clean`) ve yetim bağımlılıkları tek tıkla temizleme.
* **Yansı / Depo Yönetimi:** Aktif yansı listelerini (`mirrorlist` / `sources.list`) kolayca etkinleştirip devre dışı bırakabilme.
* **Seçilebilir Güncellemeler:** Kullanıcının yalnızca istediği paketleri seçerek güncelleyebilmesi.

---

## 📸 Ekran Görüntüleri

| Güncellemeler Listesi | Sistem Güncel Durumu | Ayarlar ve Bakım |
| :---: | :---: | :---: |
| ![Pars Update Güncellemeler](../screenshots/pars-update-1.png) | ![Pars Update Sistem Güncel](../screenshots/pars-update-2.png) | ![Pars Update Ayarlar](../screenshots/pars-update-3.png) |

---

## 🚀 Hızlı Başlangıç

### 1. Çalıştırma
```bash
# Modern Libadwaita / GTK4 arayüzü ile başlat:
./pars-update

# Arka planda kontrol et (güncelleme varsa bildirim gösterir):
./pars-update --check

# Klasik GTK3 arayüzü ile başlat:
./pars-update --gtk3
```

### 2. Tek Komutla Otomatik Kurulum
Bağımlılıkları kurup uygulamayı sisteme yüklemek için (Arch ve Debian otomatik algılanır):
```bash
sudo ./install.sh
```

### 3. Testleri Çalıştırma
```bash
python3 -m unittest discover tests
```

### 4. Kaldırma
```bash
sudo ./uninstall.sh
```

### 5. Paket Derleme
* **Arch Linux (PKGBUILD):**
  ```bash
  makepkg -si
  ```
* **Debian (.deb):**
  ```bash
  sudo apt install -y devscripts git-buildpackage
  gbp buildpackage --git-export-dir=/tmp/build/pars-update -us -uc
  ```

---

## 📚 Dokümantasyon Rehberi (Docs Index)

Projenin tüm teknik, operasyonel ve kullanıcı dokümanlarına aşağıdaki bağlantılardan ulaşabilirsiniz:

### Çekirdek ve Sistem Dokümantasyonu
* 🏗️ **[Sistem Mimarisi (ARCHITECTURE.md)](ARCHITECTURE.md)**: Core/UI katman ayrımı, GTK4 & Libadwaita yapısı, Polkit ve IPC entegrasyonu.
* 📦 **[Kurulum Kılavuzu (INSTALL.md)](INSTALL.md)**: Ayrıntılı derleme, bağımlılıklar ve kurulum adımları.
* 🛡️ **[Güvenlik Politikası (SECURITY.md)](SECURITY.md)**: Yetki ayrımı, girdi doğrulama ve güvenlik açığı bildirim süreci.
* 💻 **[Komut Satırı Referansı (CLI_REFERENCE.md)](CLI_REFERENCE.md)**: `pars-update` ve arka plan betiklerinin tüm parametreleri.

### Entegrasyon ve Yönetim Kılavuzları
* 🔗 **[Uygulama ve Masaüstü Entegrasyonu (UYGULAMA_BAGLAMA.md)](UYGULAMA_BAGLAMA.md)**: Desktop dosyaları, otomatik başlatma ve harici çağırma.
* 🌐 **[Özel Depo ve Sunucu Barındırma (SELF_HOSTING_GUIDE.md)](SELF_HOSTING_GUIDE.md)**: Kurumsal APT deposu ve `dists.json` sürüm uç noktası kurulumu.
* 💾 **[Veri ve Kota Tasarrufu (DATA_SAVING_GUIDE.md)](DATA_SAVING_GUIDE.md)**: Disk alanı ve mobil internet kotası tasarruf yöntemleri.

### Geliştirme ve Topluluk
* 🤝 **[Katkı Sağlama Rehberi (CONTRIBUTING.md)](CONTRIBUTING.md)**: PR iş akışı, kod standartları ve kurallar.
* 🧪 **[Test ve Kalite Güvencesi (TESTING.md)](TESTING.md)**: Birim, UI ve sistem testleri (17/17 test).
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
