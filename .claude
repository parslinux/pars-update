# CLAUDE.md - Pars Update Geliştirici & AI Asistan Rehberi

Bu belge, **Pars Update (`pars-update`)** projesinde kod yazarken, hata ayıklarken veya projeyi geliştirirken dikkat edilmesi gereken mimari kuralları, komutları ve geliştirme standartlarını açıklar.

---

## 1. Proje Genel Bakışı
* **Proje Adı:** Pars Update (`pars-update`)
* **Amaç:** Debian tabanlı sistemler ve Pars Linux için kullanıcı dostu, güvenli ve hafif GTK3 tabanlı sistem güncelleme yöneticisi.
* **Ana Teknolojiler:** Python 3, PyGObject (GTK+ 3, GLib, Gio), python3-apt, Polkit (pkexec), Systemd, Gettext.
* **Uygulama Kimliği:** `org.pars.update`

---

## 2. Dizin Yapısı
* `src/`: Python kaynak kodları.
  * `Main.py`: Uygulamanın giriş noktası (`Gtk.Application`).
  * `MainWindow.py`: Ana pencere mantığı, menüler, sistem tepsisi (AppIndicator) ve sinyal işleyicileri.
  * `SysActions.py`: Polkit üzerinden root haklarıyla çalışan sistem eylemleri (upgrade, autoremove, cache clean vb.).
  * `AptSourceActions.py`: `/etc/apt/sources.list` düzenleme ve onarım eylemleri (root).
  * `SystemSettings.py` & `SystemSettingsWrite.py`: `/etc/pars/pars-update.conf` sistem ayarları.
  * `UserSettings.py`: `~/.config/pars/pars-update/settings.ini` kullanıcı ayarları.
  * `Group.py`: Kullanıcıyı `pars-update` grubuna ekleme/çıkarma (parolasız kullanım).
  * `Package.py`: APT önbelleği ve paket durum sorguları.
  * `RepoDistControl.py`: Yeni dağıtım sürümü kontrolü.
  * `Utils.py`: Masaüstü ortamı tespiti ve yardımcı fonksiyonlar.
* `ui/`: Glade ile tasarlanmış XML arayüz tanımları (`MainWindow.glade`).
* `data/`: Simgeler, desktop dosyaları, Polkit kural ve yetki dosyaları, systemd servisleri.
* `debian/`: Debian paketleme yapılandırması (`control`, `rules`, `changelog`, `postinst`).
* `po/`: Çok dilli gettext çeviri dosyaları (`tr.po`, `pt.po`, `pars-update.pot`).
* `docs/`: Mimari, güvenlik, kurulum ve geliştirme dokümantasyonu.

---

## 3. Temel Geliştirme Komutları

### Bağımlılıkları Yükleme (Debian / Pardus / Pars)
```bash
sudo apt install gir1.2-glib-2.0 gir1.2-gtk-3.0 gir1.2-notify-0.7 \
    gir1.2-soup-2.4 gir1.2-vte-2.91 gir1.2-ayatanaappindicator3-0.1 \
    python3-apt python3-distro gettext
```

### Kaynaktan Çalıştırma
```bash
python3 src/Main.py
# veya tepsi (tray) modunda:
python3 src/Main.py --tray
```

### Sözdizimi ve Derleme Kontrolü
```bash
python3 -m py_compile src/*.py pars-update setup.py
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
