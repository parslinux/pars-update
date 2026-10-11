# Pars Update - Test ve Kalite Güvence Kılavuzu (TESTING.md)

Bu kılavuz, **Pars Update (`pars-update`)** uygulamasının kod değişiklikleri sonrasında nasıl test edileceğini, sözdizimi doğrulamasını ve güvenli test senaryolarını açıklar.

---

## 1. Hızlı Sözdizimi Testi (Syntax Compilation)

Tüm Python kaynak kodlarının sözdizimsel olarak hatasız olduğunu doğrulamak için:

```bash
python3 -m py_compile src/*.py pars-update setup.py
```
> Çıktı boş dönüyorsa tüm dosyaların sözdizimi geçerlidir.

---

## 2. Arayüz ve UI Bileşenleri Testi

Arayüzün GTK+ Builder ve Glade dosyasıyla sorunsuz yüklendiğini root yetkisi olmadan test edebilirsiniz:

```bash
# 1. Normal pencere testi:
python3 src/Main.py

# 2. Tepsi (Tray) simgesi ve menü testi:
python3 src/Main.py --tray

# 3. Belirli bir sayfaya doğrudan geçiş testi:
python3 src/Main.py --page updateinfo
```

### UI Test Kontrol Listesi:
- [ ] Ana pencere sorunsuz açılıyor mu?
- [ ] Sistem tepsisi simgesi (AppIndicator) sağ tıklandığında menü açılıyor mu?
- [ ] "Ayarlar" butonuna basıldığında ayarlar paneline geçiliyor mu?
- [ ] "Hakkında" penceresinde sürüm ve telif bilgileri doğru görünüyor mu?

---

## 3. Ayrıcalıklı Eylemlerin (Polkit) Test Edilmesi

Root yetkisiyle çalışan arka plan betiklerini doğrudan terminalden test edebilirsiniz:

### 3.1 APT Önbellek Temizleme Testi:
```bash
/usr/bin/pkexec python3 src/SysActions.py aptclear 1 0 0
```

### 3.2 Sistem Ayarları Yazma Testi:
```bash
/usr/bin/pkexec python3 src/SystemSettingsWrite.py write lastupdate 1700000000
```

### 3.3 Grup Üyeliği Testi:
```bash
/usr/bin/pkexec python3 src/Group.py add $USER
/usr/bin/pkexec python3 src/Group.py del $USER
```

---

## 4. Paketleme ve Kurulum Testi

Debian paketinin hatasız derlenip derlenmediğini doğrulamak için:

```bash
# Paket derleme testi:
dpkg-buildpackage -us -uc -b

# Lintian ile paket standartları denetimi:
lintian ../pars-update_*.deb
```
