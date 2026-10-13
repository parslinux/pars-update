# CLAUDE.md - Pars Update Geliştirici & AI Asistan Rehberi

Bu belge, **Pars Update (`pars-update`)** projesinde kod yazarken, hata ayıklarken veya projeyi geliştirirken dikkat edilmesi gereken mimari kuralları, komutları ve geliştirme standartlarını açıklar.

---

## 1. Proje Genel Bakışı
* **Proje Adı:** Pars Update (`pars-update`)
* **Amaç:** Pars Linux, Arch Linux ve Debian tabanlı sistemler için kullanıcı dostu, güvenli ve hafif GTK4 / Libadwaita tabanlı sistem güncelleme yöneticisi (GTK3 fallback destekli).
* **Ana Teknolojiler:** Python 3, PyGObject (GTK4, Libadwaita, GTK+ 3, GLib, Gio), Pacman & APT arka uçları, Polkit (pkexec), Systemd, Gettext.
* **Uygulama Kimliği:** `org.pars.update`

---

## 2. Dizin Yapısı
* `src/`: Python kaynak kodları.
  * `Main.py`: Giriş noktası; GTK4/Libadwaita (`MainAdw.py`) ve GTK3 (`MainWindow.py`) çalışma zamanı seçimi.
  * `MainAdw.py`: Modern `Adw.Application` ana süreç yöneticisi.
  * `core/`: Arayüzden bağımsız çekirdek servis katmanı (`UpdateEngine`, `ConfigManager`, `NotificationManager`, `TerminalRunner`).
  * `ui/`: Modern Libadwaita arayüz bileşenleri (`MainWindowAdw.py`, `PreferencesAdw.py`).
  * `PackageManagerBackend.py`: Çoklu dağıtım paket motoru (`PacmanBackend`).
  * `Package.py`: APT önbelleği ve paket durum sorguları köprüsü.
  * `MainWindow.py`: Klasik GTK3 ana penceresi (yedek fallback).
  * `SysActions.py`: Polkit üzerinden root haklarıyla çalışan sistem eylemleri (upgrade, autoremove, cache clean vb.).
  * `AptSourceActions.py`: `/etc/apt/sources.list` ve `/etc/pacman.d/mirrorlist` düzenleme eylemleri (root).
  * `SystemSettings.py` & `SystemSettingsWrite.py`: `/etc/pars/pars-update.conf` sistem ayarları.
  * `UserSettings.py`: `~/.config/pars/pars-update.json` kullanıcı ayarları.
  * `Group.py`: Kullanıcıyı `pars-update` grubuna ekleme/çıkarma (parolasız kullanım).
  * `RepoDistControl.py`: Yeni dağıtım sürümü kontrolü.
  * `Utils.py`: Masaüstü ortamı tespiti ve yardımcı fonksiyonlar.
* `ui/`: Glade ile tasarlanmış eski XML arayüz tanımları (`MainWindow.glade`).
* `data/`: Vektörel SVG simgeler, desktop dosyaları, Polkit kural ve yetki dosyaları, systemd servisleri.
* `debian/`: Debian paketleme yapılandırması (`control`, `rules`, `changelog`).
* `po/`: Çok dilli gettext çeviri dosyaları (`tr.po`, `pt.po`, `pars-update.pot`).
* `tests/`: Otomatik birim ve entegrasyon testleri (`test_arch_and_backend.py`, `test_core_and_adw.py`).
* `docs/`: Mimari, güvenlik, kurulum ve geliştirme dokümantasyonu.

---

## 3. Temel Geliştirme Komutları

### Kaynaktan Çalıştırma
```bash
# Modern Libadwaita (GTK4):
./pars-update

# Klasik GTK3 modu:
./pars-update --gtk3
```

### Testleri Çalıştırma
```bash
python3 -m unittest discover tests
```

### Sözdizimi ve Derleme Kontrolü
```bash
python3 -m py_compile src/*.py src/core/*.py src/ui/*.py pars-update setup.py
```

### Çevirileri Güncelleme
```bash
bash update-translations.sh
```

### Debian Paketi Oluşturma
```bash
sudo apt install devscripts git-buildpackage
sudo mk-build-deps -ir
gbp buildpackage --git-export-dir=/tmp/build/pars-update -us -uc
```

---

## 4. Kodlama ve Mimari Kuralları

1. **Ayrıcalık Ayrımı (Privilege Separation):**
   * GUI (`Main.py`, `MainWindow.py`) **asla root olarak çalıştırılmaz**.
   * Root gerektiren tüm işlemler `pkexec` aracılığıyla `SysActions.py`, `AptSourceActions.py`, `AutoAptUpdate.py` veya `SystemSettingsWrite.py` çağrılarak yapılır.
   * Root betiklerine gönderilen argümanlar kesinlikle doğrulanmalıdır (Input Validation).

2. **Uluslararasılaştırma (i18n):**
   * Kullanıcıya görünen her metin `_("Metin")` şeklinde gettext ile sarılmalıdır.
   * Text domain `pars-update` olarak ayarlanmalıdır.

3. **Glade ve Arayüz Düzenlemeleri:**
   * CSS sınıfları için `.pars-update-frame` kullanılmalıdır.
   * İkon referansları `pars-update*` adlandırma kuralına uymalıdır.

4. **Sürüm Yönetimi:**
   * Sürüm numarası [debian/changelog](file:///home/can/Masaüstü/projeler/mcsm/masaüstü/inceleme_düzenleme/upteda/debian/changelog) içerisindeki en üst kayıttan okunur.
