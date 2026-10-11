# Pars Update - Sistem ve Uygulama Entegrasyon Kılavuzu (UYGULAMA_BAGLAMA.md)

Bu kılavuz, **Pars Update** uygulamasının masaüstü ortamlarına (GNOME, XFCE, KDE vb.), sistem başlangıcına ve diğer yönetim araçlarına nasıl entegre edileceğini açıklar.

---

## 1. Masaüstü Başlatıcı Entegrasyonu (.desktop)

Pars Update, freedesktop.org Masaüstü Giriş Belirtimi'ne (Desktop Entry Specification) tam uyumludur:

* **Dosya Konumu:** `/usr/share/applications/org.pars.update.desktop`
* **Yapı:**
  ```ini
  [Desktop Entry]
  Name=Pars Update
  Name[tr]=Pars Güncelleyici
  Comment=Simple update application
  Comment[tr]=Basit güncelleme uygulaması
  Exec=pars-update
  Icon=pars-update
  Terminal=false
  Type=Application
  Categories=GTK;System;X-Pars-Apps;
  StartupNotify=true
  Keywords=apt;update;upgrade;pars
  ```

---

## 2. Otomatik Başlatma (Autostart Entegrasyonu)

Kullanıcı oturum açtığında arka planda sistem tepsisinde (tray) sessizce başlaması için:

* **Sistem Şablonu:** `/etc/skel/.config/autostart/org.pars.update-autostart.desktop`
* **Kullanıcı Bağlantısı:** `~/.config/autostart/org.pars.update-autostart.desktop`
* **Komut:**
  ```bash
  pars-update --tray
  ```
  `--tray` parametresi ile başlatıldığında ana pencere gizli kalır; yalnızca bildirim alanı simgesi (`AyatanaAppIndicator3`) yüklenir.

---

## 3. Komut Satırı ve D-Bus IPC Arayüzü

Pars Update, `Gtk.Application` tabanlı tekil örnek (Single-instance) modeline sahiptir. Başka bir uygulama veya betik `pars-update` komutunu çağırdığında:

| Komut | Açıklama |
| :--- | :--- |
| `pars-update` | Ana güncelleme penceresini açar (varsa öne getirir). |
| `pars-update --tray` | Arka plan tepsi modunda başlatır. |
| `pars-update --page updateinfo` | Doğrudan bekleyen güncellemeler listesi sayfasını açar. |

### Örnek: Bildirim veya Harici Betikten Çağırma
```python
import subprocess
# Harici bir araçtan güncellemeler sayfasını açtırmak için:
subprocess.Popen(["/usr/bin/pars-update", "--page", "updateinfo"])
```

---

## 4. Paket Yöneticisi Çakışma Önleme Entegrasyonu

Pars Update, sistemde aynı anda başka bir paket aracının (`apt`, `dpkg`, `synaptic`, `packagekit`) çalışıp çalışmadığını APT sistem kilidi (`/var/lib/dpkg/lock-frontend`) ile denetler:
* Eğer kilit aktifse kullanıcıya bilgilendirme penceresi sunulur.
* `dpkg` kesintisi tespit edilirse kullanıcıya tek tıkla `"Düzelt"` (`dpkg --configure -a`) seçeneği sunulur.
