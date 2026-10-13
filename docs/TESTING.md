# Pars Update - Test ve Kalite Güvence Kılavuzu (TESTING.md)

Bu kılavuz, **Pars Update (`pars-update`)** uygulamasının kod değişiklikleri sonrasında nasıl test edileceğini, otomatik birim testlerini, sözdizimi doğrulamasını ve güvenli test senaryolarını açıklar.

---

## 1. Otomatik Test Paketi (Automated Unit Tests)

Projeye eklenen otomatik test paketi, tüm mimariyi (dağıtım algılama, Pacman performansı, SVG geçerliliği, CSS sınıfları, Core servisleri ve Adw arayüz modüllerini) doğrular.

Tüm testleri çalıştırmak için:

```bash
python3 -m unittest discover tests
```

### Test Modülleri:
* **`tests/test_arch_and_backend.py`**:
  * Dağıtım algılama (`get_distro_info`, `get_package_manager`).
  * Boyut ayrıştırma (`parse_pacman_size_str`).
  * Sürüm karşılaştırma (`vercmp`).
  * Masaüstü dosyası sahiplik sorgusu (`get_appname_from_desktopfile`).
  * SVG vektör dosyalarının XML geçerliliği ve viewBox tanımları.
  * Polkit politika dosyası ve CSS tema sınıfları.
* **`tests/test_core_and_adw.py`**:
  * `UpdateEngine` başlatma, kilit denetimi ve boyut hesaplamaları.
  * `ConfigManager` kullanıcı ve sistem property'leri.
  * `NotificationManager` bildirim çağrıları ve hata toleransı.
  * `TerminalRunner` VTE süreç başlatıcı korumaları.
  * `MainWindowAdw`, `PreferencesAdw` ve `UpdateApplication` Libadwaita bileşen testleri.

---

## 2. Hızlı Sözdizimi Testi (Syntax Compilation)

Tüm Python kaynak kodlarının sözdizimsel olarak hatasız olduğunu doğrulamak için:

```bash
python3 -m py_compile src/*.py src/core/*.py src/ui/*.py pars-update setup.py
```
> Çıktı boş dönüyorsa tüm dosyaların sözdizimi geçerlidir.

---

## 3. Arayüz ve UI Bileşenleri Testi

### 3.1 Modern GTK4 / Libadwaita Modu (Varsayılan):
```bash
# 1. Normal pencere testi:
./pars-update

# 2. Arka plan kontrol modu:
./pars-update --check

# 3. Belirli bir sayfaya doğrudan geçiş:
./pars-update --page updates
./pars-update --page settings
```

### 3.2 Klasik GTK3 Modu (Geriye Dönük Uyumluluk):
```bash
# Klasik GTK3 pencere testi:
./pars-update --gtk3

# Sistem tepsisi (AppIndicator) testi:
./pars-update --gtk3 --tray
```

---

## 4. Ayrıcalıklı Eylemlerin (Polkit) Test Edilmesi

Root yetkisiyle çalışan arka plan betiklerini doğrudan terminalden test edebilirsiniz:

### 4.1 Önbellek Temizleme Testi:
```bash
/usr/bin/pkexec python3 src/SysActions.py aptclear 1 0 0
```

### 4.2 Sistem Ayarları Yazma Testi:
```bash
/usr/bin/pkexec python3 src/SystemSettingsWrite.py write lastupdate 1700000000
```

### 4.3 Grup Üyeliği Testi:
```bash
/usr/bin/pkexec python3 src/Group.py add $USER
/usr/bin/pkexec python3 src/Group.py del $USER
```

---

## 5. Paket Derleme Testi

* **Arch Linux (PKGBUILD):**
  ```bash
  makepkg -f
  ```
* **Debian (.deb):**
  ```bash
  dpkg-buildpackage -us -uc -b
  lintian ../pars-update_*.deb
  ```
