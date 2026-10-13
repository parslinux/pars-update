# Pars Update - Sistem ve Yazılım Mimarisi (ARCHITECTURE.md)

Bu belge, **Pars Update** uygulamasının mimarisini, katmanlı yazılım tasarımını, bileşenler arası veri akışını, ayrıcalık yönetimini ve sistem entegrasyonlarını ayrıntılı olarak açıklamaktadır.

---

## 1. Yüksek Düzey Mimari (High-Level Architecture)

Pars Update, modülerlik ve güvenlik ilkeleri gereği **katmanlı ve yetki ayrımlı (Privilege-Separated & Layered)** bir mimariyle tasarlanmıştır:

```
+-----------------------------------------------------------------------------------+
|                         Kullanıcı Oturumu (Unprivileged)                          |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                  Giriş ve Çalışma Zamanı Katmanı (Entry Layer)              |  |
|  |   pars-update  -->  Main.py (GTK4 / Libadwaita tespiti veya --gtk3 seçimi) |  |
|  +-----------------------------------------------------------------------------+  |
|               |                                                     |             |
|       (Varsayılan / GTK4)                                   (Fallback / GTK3)     |
|               v                                                     v             |
|  +---------------------------+                         +-----------------------+  |
|  |   Arayüz Katmanı (src/ui)  |                         |   Eski GTK3 Katmanı   |  |
|  |   - MainWindowAdw.py      |                         |   - MainWindow.py     |  |
|  |   - PreferencesAdw.py     |                         |   - ui/MainWindow.    |  |
|  |   (Libadwaita Widgets)    |                         |     glade             |  |
|  +---------------------------+                         +-----------------------+  |
|               \                                                     /             |
|                +-------------------------+-------------------------+              |
|                                          |                                        |
|                                          v                                        |
|  +-----------------------------------------------------------------------------+  |
|  |                     Çekirdek Servis Katmanı (src/core)                      |  |
|  |   - UpdateEngine.py       : Asenkron sorgulama, kilit denetimi, boyutlar    |  |
|  |   - ConfigManager.py      : UserSettings & SystemSettings property sarmala. |  |
|  |   - NotificationManager.py: Masaüstü bildirimleri (Libnotify)               |  |
|  |   - TerminalRunner.py     : GTK4 VTE 3.91 terminal süreç yürütücüsü         |  |
|  +-----------------------------------------------------------------------------+  |
|                                          |                                        |
|                                          v                                        |
|  +-----------------------------------------------------------------------------+  |
|  |                     Paket Motoru Katmanı (Engine & Backends)                |  |
|  |   - PackageManagerBackend.py (PacmanBackend - Arch Linux / checkupdates)    |  |
|  |   - Package.py               (Debian / python3-apt Cache köprüsü)           |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
                                           |
                                  pkexec / Polkit IPC
                                           |
+-----------------------------------------------------------------------------------+
|                         Sistem Katmanı (Root / Privileged)                        |
|                                                                                   |
|   +-----------------------+  +-----------------------+  +---------------------+   |
|   |     SysActions.py     |  |  AptSourceActions.py  |  |      Group.py       |   |
|   | (pacman -Syu / clean) |  | (mirrorlist / sources)|  | (pars-update grubu) |   |
|   | (apt upgrade / clean) |  | (güvenli satır filtres|  | (parolasız polkit)  |   |
|   +-----------------------+  +-----------------------+  +---------------------+   |
|               |                          |                          |             |
|               v                          v                          v             |
|   +-----------------------+  +-----------------------+  +---------------------+   |
|   |  /etc/pars/           |  |  /var/log/            |  | /etc/polkit-1/      |   |
|   |  pars-update.conf     |  |  pars-upgrade.log     |  | rules.d/            |   |
|   +-----------------------+  +-----------------------+  +---------------------+   |
+-----------------------------------------------------------------------------------+
```

---

## 2. Katmanlar ve Bileşenlerin Görevleri

### 2.1 Giriş ve Çalışma Zamanı Katmanı
* **`pars-update` (Başlatıcı Betik):**
  * Uygulamanın `/usr/bin/pars-update` üzerinden veya yerel geliştirme dizininden doğrudan çalıştırılmasını sağlar.
* **`src/Main.py`:**
  * Çalışma ortamında GTK4 ve Libadwaita (`Adw.Application`) kütüphanelerinin varlığını kontrol eder.
  * Kullanıcı `--gtk3` veya `--legacy` argümanı vermişse ya da sistemde GTK4 bulunmuyorsa, süreci çökertmeden temiz şekilde eski GTK3 `MainWindow` modülüne yönlendirir.
* **`src/MainAdw.py`:**
  * GTK4 `Adw.Application` (`org.pars.update`) sınıfını barındırır.
  * `-t, --tray`, `-c, --check` ve `-p, --page` argümanlarını işler.
  * `do_activate` ve `do_command_line` sinyalleriyle tekil örnek (single-instance) yönetimini sağlar.

### 2.2 Kullanıcı Arayüzü Katmanı (`src/ui/`)
* **`src/ui/MainWindowAdw.py`:**
  * `Adw.ApplicationWindow`, `Adw.ToolbarView` ve `Adw.HeaderBar` kullanır.
  * `Adw.ViewStack` ile 5 farklı uygulama durumunu akıcı şekilde yönetir:
    1. `uptodate`: Sistem güncel durumu ve son kontrol tarihi.
    2. `checking`: Asenkron sorgulama sırasında dönen spinner ekranı.
    3. `updates`: Seçilebilir paket listesi, sürüm geçişleri (`1.0.0 -> 1.0.1`) ve indirme boyutu rozetleri.
    4. `terminal`: Yükseltme işlemi sırasında canlı VTE terminal çıktısı.
    5. `error`: Kilit veya ağ hatası durumu; tek tıkla kilit temizleme ve tekrar deneme butonları.
  * `Adw.ToastOverlay` ile kullanıcıya modern geri bildirim bildirimleri gösterir.
* **`src/ui/PreferencesAdw.py`:**
  * `Adw.PreferencesWindow` sınıfından türetilmiştir.
  * **Genel:** Kontrol periyodu (Günlük, Haftalık, Asla), sistem açılışında otomatik başlama ve masaüstü bildirim anahtarları.
  * **Depolar / Aynalar:** Arch Linux'ta aktif Pacman yansıları, Debian'da APT kaynakları listelenir; kullanıcı anahtarlarla depoları açıp kapatabilir.
  * **Bakım:** Önbellek temizliği (`pacman -Sc` / `apt clean`) ve yetim paket temizliği (`removeauto`).

### 2.3 Çekirdek Servis Katmanı (`src/core/`)
* **`src/core/UpdateEngine.py`:**
  * Tüm paket sorgulama ve kilit denetimlerini arayüzden bağımsız olarak yürütür.
  * `check_updates_async`: GLib iş parçacığı (`threading.Thread`) açarak arka planda depoları sorgular; UI'ın donmasını engeller.
  * `calculate_sizes`: Kullanıcının işaretlemediği paketleri dışarıda tutarak (`keep_list`) dinamik olarak indirme ve kurulum boyutunu hesaplar.
* **`src/core/ConfigManager.py`:**
  * Kullanıcı ayarları (`~/.config/pars/pars-update.json`) ve sistem ayarlarını (`/etc/pars/pars-update.conf`) tek bir API arkasında toplar.
* **`src/core/NotificationManager.py`:**
  * `libnotify` tabanlı masaüstü bildirimlerini soyutlar.
* **`src/core/TerminalRunner.py`:**
  * GTK4 VTE 3.91 terminal süreç yürütücüsüdür. PTY oluşturur, komutu asenkron başlatır (`spawn_async`) ve süreç bittiğinde `child-exited` sinyaliyle geri çağrımı tetikler.

### 2.4 Paket Motoru Katmanı (Multi-Backend)
* **`PackageManagerBackend.py` (PacmanBackend):**
  * Arch Linux üzerinde `pacman`, `checkupdates` (`pacman-contrib`) araçlarıyla çalışır.
  * `_query_pacman_si_batch`: Tüm güncellenebilir paket bilgilerini tek seferde çekerek kontrol süresini milisaniyelere indirir.
  * `vercmp` ile güvenilir sürüm karşılaştırması yapar.
* **`Package.py`:**
  * Debian üzerinde `python3-apt` (`apt.Cache()`) arayüzünü bağlar.

### 2.5 Ayrıcalıklı Sistem Katmanı (Privileged Root)
* **`SysActions.py` (`pkexec`):**
  * Paket yükseltme, temizleme, kilit çözme işlemlerini root yetkisiyle icra eder. Kilit silme öncesinde çalışan `pacman` sürecini denetler.
* **`AptSourceActions.py` (`pkexec`):**
  * `/etc/apt/sources.list` veya `/etc/pacman.d/mirrorlist` dosyalarını güvenli biçimde günceller.
* **`Group.py` (`pkexec`):**
  * Kullanıcıyı `pars-update` grubuna ekleyerek parolasız polkit yetkisi tanır.

---

## 3. Güvenli Çevrimdışı Güncelleme Mimarisi (Offline Safe Upgrade)

Büyük sistem güncellemelerinde oturumun çökmesini önlemek için Pars Update, Systemd çevrimdışı güncelleme standardını destekler:

1. Paketler kullanıcı oturumundayken indirilir (`--download-only`).
2. `/system-update` tetikleyici dosyası oluşturulur.
3. Sistem yeniden başlatıldığında Plymouth açılış ekranı altında `pars-safeupgrade.service` devreye girer.
4. Paketler hiçbir grafik oturumu açık değilken kurulur ve sistem temiz şekilde yeniden başlar.
