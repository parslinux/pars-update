# Pars Update - Değişiklik Günlüğü (CHANGELOG.md)

Bu belgede **Pars Update** projesinin tüm sürümlerine ait değişiklikler, yeni özellikler ve hata düzeltmeleri yer almaktadır.

---

## [1.4.4] - 2026-10-14
### Eklendi & Yenilendi (GTK4 / Libadwaita Rewrite, Core Ayrımı, Arch Linux & Yeni Vektörel Görsel Kimlik)
* **Çekirdek (Core) ve Arayüz (UI) Katman Ayrımı:**
  * Eski 2.765 satırlık monolitik `MainWindow.py` yapısı parçalandı; iş mantığı ve paket yönetimi bağımsız `src/core/` katmanına aktarıldı.
  * `src/core/UpdateEngine.py`: UI bağımsız paket güncelleme denetimi, kilit kontrolü, indirme/kurulum boyut hesaplaması ve asenkron GLib iş parçacığı yönetimi.
  * `src/core/ConfigManager.py`: Kullanıcı (`UserSettings`) ve sistem (`SystemSettings`) yapılandırmalarını birleştiren temiz property sarmalayıcısı.
  * `src/core/NotificationManager.py`: `libnotify` tabanlı masaüstü bildirim yöneticisi.
  * `src/core/TerminalRunner.py`: GTK4 VTE 3.91 terminal süreç yürütücüsü ile kod tekrarlarının giderilmesi.
* **Modern GTK4 & Libadwaita Arayüzü (`src/ui/`):**
  * `src/ui/MainWindowAdw.py`: `Adw.ToolbarView`, `Adw.HeaderBar`, `Adw.ViewStack` (sayfalar: `uptodate`, `checking`, `updates`, `terminal`, `error`) ve `Adw.ToastOverlay` ile modern GNOME HIG standartlarında arayüz (~450 satır).
  * `src/ui/PreferencesAdw.py`: `Adw.PreferencesWindow` tabanlı Genel Ayarlar, Aynalar/Depolar ve Sistem Bakımı (önbellek ve yetim paket temizliği) sayfaları.
* **Dinamik Çalışma Zamanı & GTK3 Fallback Desteği:**
  * `src/Main.py` varsayılan olarak `src/MainAdw.py` ile modern Libadwaita uygulamasını çalıştırır.
  * `--gtk3` veya `--legacy` parametresi verildiğinde veya GTK4 bulunmayan eski sistemlerde otomatik ve hatasız olarak klasik GTK3 `MainWindow` arayüzüne düşer.
* **Yeni Pars Linux Logo ve İkon Seti (Vektörel SVG):**
  * `data/pars-update.svg`: 128x128 squircle, kraliyet mavisi gradyanlı modern uygulama ikonu ve 3D derinlikli döngüsel güncelleme sembolü.
  * `data/pars-update-symbolic.svg` & `data/pars-update-available-symbolic.svg`: Tepsi ve panel için yüksek okunurluklu minimal sembolik simgeler.
  * `data/pars-update-uptodate.svg`: "Sisteminiz Güncel" ekranı için yeşil koruma kalkanı ve onay imi vektörel illüstrasyonu.
  * `data/pars-update-cantconnect.svg`: Bağlantı hatası ekranı için modern bulut ve uyarı illüstrasyonu.
  * `data/pars-update-inprogress-symbolic.svg` & `data/pars-update-error-symbolic.svg`: Durum simgeleri güncellendi.
* **Modern CSS Teması (`data/style.css`):**
  * `.suggested-action`, `.destructive-action`, `.pill` butonları, durum rozetleri ve modern kenarlıklar eklendi.
* **Arch Linux (Pacman) Motor İyileştirmeleri:**
  * **Aday Sürüm Önbellek Düzeltmesi:** `_fetch_upgrades_raw` içerisinde `_upgradable_cache` güncellenerek `candidate_version` sorgularının en güncel sürümü döndürmesi sağlandı.
  * **Toplu Paket Bilgisi Sorgulama (Batch -Si):** `_query_pacman_si_batch` ile tek `pacman -Si` çağrısıyla tüm paket bilgileri çekilerek güncelleme kontrol süresi 10 kat hızlandırıldı.
  * **Desktop Dosyası Sahiplik Tespiti:** `get_appname_from_desktopfile` mutlak yol ve `/usr/share/applications` desteğiyle güçlendirildi.
  * **Kilit Güvenliği:** `AptSourceActions.py` ve `SysActions.py` kilit temizleme işleminden önce `pgrep -x pacman` denetimi yaparak çalışan süreci korumaya aldı.
* **Paketleme ve Bağımlılık Güncellemeleri:**
  * `setup.py`, `PKGBUILD` ve `debian/control` içine `gtk4`, `libadwaita`, `vte4` bağımlılıkları ve `src/core/`, `src/ui/` dosya yolları eklendi.
* **Kapsamlı Otomatik Test Paketi:**
  * `tests/test_arch_and_backend.py` ve `tests/test_core_and_adw.py` ile 17 birim/entegrasyon testi oluşturuldu (%100 başarı).

---

## [0.7.1] - 2026-10-12
### Değiştirildi & Yenilendi (Rebranding)
* Proje adı ve paket adı **pars-update** olarak belirlendi.
* Uygulama kimliği (`application_id`) `org.pars.update` olarak güncellendi.
* Masaüstü çalıştırma dosyaları `data/org.pars.update.desktop` ve `data/org.pars.update-autostart.desktop` olarak uyarlandı.
* Polkit yetki politikası `data/org.pars.pkexec.pars-update.policy` ve yetki kuralları `data/pars-update-group.rules` olarak güncellendi.
* Çevrimdışı güvenli güncelleme betiği (`pars-safeupgrade-template.sh`) ve systemd servisi (`pars-safeupgrade.service`) uyarlandı.
* Arayüz (`ui/MainWindow.glade`), simgeler (`data/pars-update*.svg`) ve CSS sınıfları (`.pars-update-frame`) yeni marka ile eşleştirildi.
* Dağıtım tespiti Pars Linux (`pars`) kimliği ile uyumlu hale getirildi ve `data/sources.json` içine Pars desteği eklendi.
* Türkçe ve Portekizce çeviri dosyaları güncellendi.

---

## [0.7.0] - 2026-07-21
### Eklendi
* Portekizce çeviriler güncellendi.
* KDE masaüstü için bildirim ve uygulama simgesi uyumluluk yamaları eklendi.
* Güvenli çevrimdışı yükseltme için dpkg ve kaynak listesi girdi doğrulama kuralları (input validation) eklendi.
* `AptSourceActions.py` bağımsız bir eylem olarak ayrıştırıldı ve Polkit politikası tanımlandı.

---

## [0.6.6] - 2026-05-05
### Düzeltildi
* Dağıtım sürüm kontrolü (repo dist control) URL kontrol mantığı iyileştirildi.

---

## [0.6.5] - 2026-03-24
### Eklendi
* İzleme (monitoring) mekanizmasına devam eden güncelleme kontrolleri eklendi.

---

## [0.6.4] - 2026-03-24
### Düzeltildi
* `SystemSettingsWrite` argüman denetimleri güçlendirildi.
* Kullanılmayan eski otomatik yükseltme fonksiyonları temizlendi.

---

## [0.6.3] - 2026-03-06
### İyileştirildi
* Uygulama açıkken gereksiz bildirim gönderilmesi engellendi.
* Yükseltme işlemi için yeni çıkış kodları (exit codes) kontrol mekanizması eklendi.

---

## [0.6.2] - 2025-11-24
### Güvenlik & Sistem
* Eskiyen `.pkla` Polkit kural formatı modern `.rules` JavaScript formatına dönüştürüldü.

---

## [0.6.0] - 2025-10-08
### Eklendi
* Bağlantı hatası durumunda kullanıcıyı bilgilendiren `cantconnect` sayfası ve görseli eklendi.
* Çevrimdışı yükseltmede Plymouth önyükleme teması kontrolü eklendi.
* `sources.json` statik kaynak haritası eklendi.

---

## [0.5.0] - 2024-09-03
### Eklendi
* Ayarlar sayfasına paket yöneticisi temizlik araçları (önbellek silme, artık paket temizliği) eklendi.
* `pars-update` grubu üzerinden parolasız kullanım seçeneği eklendi.

---

## [0.4.0] - 2024-08-06
### Eklendi
* Güncellemeler listesinde tek tek paket seçebilme (Selectable Updates) ve bağımlılık zinciri kontrolü eklendi.

---

## [0.1.0] - 2023-08-20
* İlk kararlı sürüm yayınlandı. GTK3 arayüzü, AppIndicator sistem tepsisi desteği ve APT önbellek entegrasyonu sağlandı.
