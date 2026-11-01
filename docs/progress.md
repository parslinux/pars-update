# Pars Update - İlerleme ve Yol Haritası (progress.md)

Bu belge, **Pars Update (`pars-update`)** projesinde tamamlanan kilometre taşlarını, mevcut durumu ve gelecek geliştirme hedeflerini özetler.

---

## 1. Tamamlanan Kilometre Taşları (Completed)

### Mimari ve Çekirdek (Core) Dönüşümü
- [x] **Core & UI Katman Ayrımı (`src/core/`):**
  - `UpdateEngine`: Arayüzden bağımsız güncelleme denetimi, kilit kontrolü, indirme/kurulum boyutu hesaplamaları ve asenkron GLib iş parçacığı yönetimi.
  - `ConfigManager`: Kullanıcı ve sistem yapılandırmalarını birleştiren temiz property sarmalayıcısı.
  - `NotificationManager`: Libnotify tabanlı bildirim soyutlaması.
  - `TerminalRunner`: VTE 3.91 terminal süreç yürütücüsü ile kod tekrarlarının ortadan kaldırılması.
- [x] **Çoklu Dağıtım ve Paket Yöneticisi Desteği:**
  - Arch Linux: `pacman`, `checkupdates` (`pacman-contrib`), toplu paket sorgulama (`_query_pacman_si_batch`), `vercmp` ve `db.lck` kilit koruması.
  - Debian / Pars: `python3-apt` (`apt.Cache`) ve `dpkg` tam uyumluluğu.
  - Dağıtımdan bağımsız grup ve yetki yönetimi (`pars-update` grubu).

### Kullanıcı Arayüzü (GTK4 & Libadwaita)
- [x] **Modern Libadwaita Arayüzü (`src/ui/`):**
  - `MainWindowAdw`: `Adw.ToolbarView`, `Adw.HeaderBar`, `Adw.ViewStack` (sayfalar: `uptodate`, `checking`, `updates`, `terminal`, `error`) ve `Adw.ToastOverlay`.
  - `PreferencesAdw`: `Adw.PreferencesWindow` ile Genel Ayarlar, Aynalar/Depolar ve Sistem Bakımı (önbellek ve yetim paket temizliği).
- [x] **Geriye Dönük Uyumluluk (GTK3 Fallback):**
  - `Main.py` üzerinden GTK4/Libadwaita varsayılan çalışırken, `--gtk3` bayrağıyla veya GTK4 bulunmayan eski sistemlerde otomatik GTK3 fallback desteği.
- [x] **Vektörel SVG Görsel Kimlik:**
  - 7 adet modern SVG vektör ikonu (`pars-update.svg`, sembolik simgeler, `pars-update-uptodate.svg`, `pars-update-cantconnect.svg`).
  - Modern Libadwaita uyumlu CSS sınıfları (`style.css`).

### Güvenlik ve Sistem Entegrasyonu
- [x] **Güvenli Çevrimdışı Güncelleme:** Systemd `system-update.target` ve Plymouth açılış ekranı entegrasyonu.
- [x] **Yetki Ayrımı:** Polkit JavaScript kuralları (`.rules`) ve `pars-update` grubu ile güvenli yetkilendirme.
- [x] **Seçilebilir Güncellemeler:** Kullanıcının güncellenecek paketleri tek tek seçebilmesi.
- [x] **Pars Update Rebranding:** Kod tabanının Pars Update (`pars-update`, `org.pars.update`) olarak tam uyarlanması.

### Kalite Güvencesi ve Testler
- [x] **Kapsamlı Test Paketi (`tests/`):** 23 birim ve entegrasyon testi ile %100 başarı oranı (`test_arch_and_backend.py`, `test_core_and_adw.py`).

---

## 2. Mevcut Durum (Current Status - v1.5.0)
* **Mimari:** Çekirdek (Core) ve UI katmanları tamamen ayrıştırıldı.
* **Modern Arayüz:** GTK4 ve Libadwaita tam olarak entegre edildi, eski GTK3 arayüzü yedek olarak korundu.
* **Ağ ve Kota Koruması:** `NetworkMonitor` ve `Adw.Banner` ile kotalı/mobil ağlarda veri tüketimi kontrolü sağlandı.
* **Çekirdek Uyarısı:** Kritik paket güncellemelerinde yeniden başlatma rozeti ve işlem sonu uyarı diyaloğu eklendi.
* **Paket Detayları & Changelog:** Her paket için sürüm, açıklama, bağımlılıklar, web bağlantısı ve değişiklik günlüğü penceresi entegre edildi.
* **Dağıtım Desteği:** Hem Arch Linux hem de Debian/Pars Linux üzerinde tam performansla yerel araçlarla çalışmaktadır.
* **Paketleme:** `setup.py`, `PKGBUILD` ve `debian/control` yeni bağımlılıklar ve dizin yapısıyla güncellendi.

---

## 3. Gelecek Yol Haritası (Future Roadmap)

### Kısa Vadeli Hedefler (v1.5.0) - TAMAMLANDI ✅
- [x] **NetworkManager Entegrasyonu:** Mobil / kotalı ağ tespit edildiğinde otomatik indirmeyi duraklatma ve kullanıcıyı uyarma (`NetworkMonitor`, `Adw.Banner`).
- [x] **Çekirdek (Kernel) Güncelleme Bildirimi:** Sistem yeniden başlatma gerektiren çekirdek veya glibc güncellemelerinde yeniden başlatma rozeti gösterme (`requires_reboot`, `.badge-reboot`, `Adw.MessageDialog`).
- [x] **Detaylı Paket Değişiklik Günlüğü (Changelog Görüntüleyici):** Seçilen paketin sürüm notlarını ve detaylarını arayüz içinden doğrudan görüntüleme (`get_package_details`, `Adw.Window`).

### Uzun Vadeli Hedefler (v2.0.0+)
- [ ] **Flatpak & Snap Desteği:** Sistem paketlerinin yanı sıra kurulu sandbox uygulamalarının güncellemelerini de birleşik ekranda listeleme.
- [ ] **Otomatik Arka Plan İndirme:** Kullanıcının belirlediği saatlerde (ör. gece saatlerinde) güncellemeleri sessizce indirip hazır etme.
- [ ] **Dağıtım Sürüm Yükseltme Asistanı (Adw Port):** Ana dağıtım sürümü yükseltmelerini (ör. Pars 2 -> Pars 3) Libadwaita asistanı ile yönetme.
