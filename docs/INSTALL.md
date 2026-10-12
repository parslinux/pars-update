# Pars Update - Kurulum Kılavuzu (INSTALL.md)

Bu kılavuz, **Pars Update (`pars-update`)** uygulamasının bağımlılıklarının yüklenmesini, kaynaktan çalıştırılmasını ve Debian/Pars paketi olarak derlenip sisteme kurulmasını adım adım açıklar.

---

## 1. Otomatik Kurulum, Çalıştırma ve Kaldırma Betikleri (Tavsiye Edilen)

Proje kök dizininde hazır bulunan `.sh` betikleri ile tüm işlemleri tek komutla yapabilirsiniz:

### 1.1 Otomatik Kurulum (install.sh)
Bağımlılıkları kontrol eder, eksik paketleri yükler, çevirileri derler, polkit kurallarını ve sistem gruplarını ayarlar:
```bash
sudo ./install.sh
```

### 1.2 Kolay Çalıştırma (run.sh)
Gerekli bağımlılıkları kontrol eder ve uygulamayı çalıştırır:
```bash
# Normal pencere modunda:
./run.sh

# Sistem tepsisi modunda:
./run.sh --tray

# Doğrudan güncellemeler sayfasında:
./run.sh --page updateinfo
```

### 1.3 Temiz Kaldırma (uninstall.sh)
Sistemdeki tüm Pars Update ikili dosyalarını, simgelerini, polkit kurallarını ve servislerini güvenle temizler:
```bash
sudo ./uninstall.sh
```

---

## 2. Sistem Gereksinimleri
* **İşletim Sistemi:** 
  * Debian 11/12+, Pars Linux veya Ubuntu 20.04+ (APT tabanı)
  * Arch Linux, Manjaro, EndeavourOS, Garuda (Pacman tabanı)
* **Python:** Python 3.8 veya üzeri
* **Masaüstü Ortamı:** GNOME, XFCE, KDE Plasma, MATE, Cinnamon veya LXQt

---

## 3. Gerekli Bağımlılıkların Manuel Kurulması

### 3.1 Arch Linux (Pacman)
```bash
sudo pacman -S --needed \
    python \
    python-setuptools \
    python-gobject \
    gtk3 \
    libnotify \
    libsoup \
    vte3 \
    libappindicator-gtk3 \
    polkit \
    gettext \
    pacman-contrib
```

### 3.2 Debian / Ubuntu / Pars (APT)
```bash
sudo apt update
sudo apt install -y \
    python3 \
    python3-apt \
    python3-distro \
    gir1.2-glib-2.0 \
    gir1.2-gtk-3.0 \
    gir1.2-notify-0.7 \
    gir1.2-soup-2.4 \
    gir1.2-vte-2.91 \
    gir1.2-ayatanaappindicator3-0.1 \
    policykit-1 \
    gettext
```

---

## 3. Kaynaktan Çalıştırma (Geliştirici Modu)

Uygulama kaynak kodunu klonladıktan sonra sisteme kurmadan doğrudan test edebilirsiniz:

```bash
cd /home/can/Masaüstü/projeler/mcsm/masaüstü/inceleme_düzenleme/upteda

# Normal pencere modunda çalıştırma:
python3 src/Main.py

# Sistem tepsisi (tray) modunda arka planda başlatma:
python3 src/Main.py --tray

# Doğrudan güncelleme sayfasına gitme:
python3 src/Main.py --page updateinfo
```

---

## 4. Debian (.deb) Paketi Oluşturma ve Kurma

Resmi Debian paketleme standartlarına uygun `.deb` ikili paketi üretmek için:

### 4.1 Derleme Araçlarını Yükleyin
```bash
sudo apt install -y devscripts git-buildpackage debhelper dh-python python3-all python3-setuptools
```

### 4.2 Paketi Derleyin
```bash
# Proje kök dizininde:
gbp buildpackage --git-export-dir=/tmp/build/pars-update -us -uc
# Veya doğrudan dpkg-buildpackage ile:
dpkg-buildpackage -us -uc -b
```

### 4.3 Oluşan Paketi Kurun
```bash
sudo apt install /tmp/build/pars-update_*.deb
# veya üst dizinde oluştuysa:
sudo apt install ../pars-update_*.deb
```

---

## 5. Arch Linux Paketi Oluşturma ve Kurma (PKGBUILD)

Arch Linux üzerinde standart paket oluşturup kurmak için:

```bash
# Proje kök dizininde:
makepkg -si
```

Veya `PKGBUILD` kullanarak AUR paketi olarak dağıtabilirsiniz.

---

## 6. `setup.py` ile Yerel Kurulum (Geliştirme Amaçlı)

Paket yöneticisi haricinde doğrudan `/usr/local` veya `/usr` altına kurmak için:

```bash
sudo python3 setup.py install --prefix=/usr
```

Kurulum sonrasında polkit kurallarının devreye girmesi için polkit servisini yeniden başlatabilirsiniz:
```bash
sudo systemctl restart polkit
```

---

## 6. Parolasız Güncelleme Grubunun Etkinleştirilmesi

Kullanıcıların her güncellemede root parolası girmeden güncellemeyi başlatabilmesi için `pars-update` sistem grubu kullanılır:

```bash
# Grubu oluşturun (paket kurulumu yapıldıysa otomatik oluşur):
sudo addgroup --system pars-update

# Kullanıcınızı bu gruba ekleyin:
sudo adduser $USER pars-update
```
> [!NOTE]
> Grup üyeliğinin geçerli olması için oturumu kapatıp yeniden açmanız gerekmektedir.
