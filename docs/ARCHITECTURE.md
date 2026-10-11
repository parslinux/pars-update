# Pars Update - Sistem ve Yazılım Mimarisi (ARCHITECTURE.md)

Bu belge, **Pars Update** uygulamasının mimarisini, bileşenler arası veri akışını, ayrıcalık yönetimini ve sistem entegrasyonlarını ayrıntılı olarak açıklamaktadır.

---

## 1. Yüksek Düzey Mimari (High-Level Architecture)

Pars Update, güvenlik ilkeleri gereği **çift katmanlı (Privilege-Separated)** bir mimariyle tasarlanmıştır:
1. **Kullanıcı Katmanı (Yetkisiz GUI Süreci):** Kullanıcı oturumu altında çalışan, masaüstü arayüzünü (GTK3) ve sistem tepsisi göstergesini (AppIndicator) barındıran süreç.
2. **Sistem Katmanı (Ayrıcalıklı Arka Plan Süreci):** Polkit (`pkexec`) yetkilendirmesiyle root izinleriyle çalışan, paket yöneticisini (`apt`, `dpkg`) ve sistem ayarlarını yöneten betikler.

```
+-----------------------------------------------------------+
|              Kullanıcı Oturumu (Unprivileged)             |
|                                                           |
|   +-------------------+         +---------------------+   |
|   |   Main.py (App)   | <-----> |   MainWindow.py     |   |
|   +-------------------+         +---------------------+   |
|             |                              |              |
|             v                              v              |
|   +-------------------+         +---------------------+   |
|   |  UserSettings.py  |         |      Package.py     |   |
|   | (~/.config/pars/) |         |    (python3-apt)    |   |
|   +-------------------+         +---------------------+   |
+-----------------------------------------------------------+
                              |
                     pkexec / D-Bus
                              |
+-----------------------------------------------------------+
|               Root / Sistem Katmanı (Privileged)          |
|                                                           |
|   +----------------------+     +----------------------+   |
|   |    SysActions.py     |     |  AptSourceActions.py |   |
|   |  (apt upgrade, clean)|     | (sources.list onarım)|   |
|   +----------------------+     +----------------------+   |
|             |                              |              |
|             v                              v              |
|   +----------------------+     +----------------------+   |
|   |  /etc/pars/          |     |  /var/log/           |   |
|   |  pars-update.conf    |     |  pars-upgrade.log    |   |
|   +----------------------+     +----------------------+   |
+-----------------------------------------------------------+
```

---

## 2. Bileşenler ve Görevleri

### 2.1 Arayüz ve Sunum Katmanı
* **`Main.py`:**
  * GTK+ `Gtk.Application` sınıfını uygular (`org.pars.update`).
  * `--tray` (yalnızca sistem tepsisinde başlat) ve `--page <sayfa_adı>` argümanlarını işler.
  * Tekil örnek (Single-instance) denetimi yapar; uygulama zaten çalışıyorsa mevcut pencereyi öne getirir.
* **`MainWindow.py`:**
  * Glade XML tanımından (`ui/MainWindow.glade`) arayüz bileşenlerini yükler.
  * Paket yükseltme, artık paket temizliği, APT kaynak listesi düzeltme ve ayarlar sayfalarını yönetir.
  * Terminal çıktılarını kullanıcıya canlı göstermek için `Vte.Terminal` bileşenini kullanır.
  * Sistem tepsisi simgesini (`AyatanaAppIndicator3`) ve masaüstü bildirimlerini (`Notify`) kontrol eder.

### 2.2 Veri ve Paket Yönetimi Katmanı
* **`Package.py`:**
  * `apt.Cache()` API'sini kullanarak kurulabilir, güncellenebilir ve kaldırılabilir paket listelerini sorgular.
  * Gerekli indirme boyutunu ve disk alanı değişimini hesaplar.
* **`RepoDistControl.py`:**
  * Dağıtım sunucusundaki `dists.json` dosyasını çekerek ana sürüm yükseltmesi (Distribution Upgrade) olup olmadığını kontrol eder.

### 2.3 Sistem ve Ayrıcalıklı Eylemler Katmanı
* **`SysActions.py`:**
  * `pkexec` üzerinden çağrılır.
  * `apt update`, `apt full-upgrade`, `apt autoremove`, `dpkg --configure -a` ve `apt clean` operasyonlarını icra eder.
  * Çevrimdışı güvenli güncelleme (`distupgradeoffline`) mekanizmasını başlatır.
* **`AptSourceActions.py`:**
  * `/etc/apt/sources.list` ve `/etc/apt/sources.list.d/` yapılandırmalarını güvenli biçimde düzenler veya varsayılanlara sıfırlar.
  * Güvenlik filtresi (`is_safe_sources`): Zararlı kaynak satırlarını (ör. `trusted=yes`, `file://`) engeller.
* **`SystemSettings.py` & `SystemSettingsWrite.py`:**
  * `/etc/pars/pars-update.conf` sistem çapındaki yapılandırmasını yönetir.
* **`Group.py`:**
  * Kullanıcının `pars-update` grubuna eklenmesini veya çıkarılmasını sağlar (Polkit parolasız kullanım).

---

## 3. Güvenli Çevrimdışı Güncelleme Mimarisi (Offline Safe Upgrade)

Büyük sistem güncellemelerinde oturumun çökmesini önlemek için Pars Update, Systemd çevrimdışı güncelleme standardını destekler:

1. Paketler kullanıcı oturumundayken `/var/cache/apt/archives/` dizinine indirilir (`--download-only`).
2. `/system-update` tetikleyici dosyası oluşturulur.
3. `pars-safeupgrade.service`, `system-update.target.wants` altına sembolik bağ ile bağlanır.
4. Sistem yeniden başlatıldığında, masaüstü ortamı açılmadan önce Systemd `system-update.target` devreye girer.
5. Plymouth açılış ekranı üzerinden ilerleme yüzdesi gösterilerek paketler kurulur.
6. İşlem tamamlandığında `/var/log/pars-upgrade.log` dosyasına rapor yazılır ve makine normal şekilde açılır.

---

## 4. Yetkilendirme Modeli (Polkit Integration)

* **Yetki Politikası:** `data/org.pars.pkexec.pars-update.policy`
  * Eylemler `org.pars.pkexec.pars-update-*` kimliğiyle tanımlıdır.
  * Her eylem hedef Python betiğinin tam yoluna (`/usr/share/pars/pars-update/src/...`) bağlanmıştır.
* **Grup İzni Kuralı:** `data/pars-update-group.rules`
  * Eğer kullanıcı `pars-update` grubunda ise, parola girmeden (`polkit.Result.YES`) güncelleme yapabilir.

---

## 5. Yapılandırma Dosyaları Hiyerarşisi

| Düzey | Konum | Amaç |
| :--- | :--- | :--- |
| **Sistem Ayarları** | `/etc/pars/pars-update.conf` | Yönetici tarafından belirlenen global kontrol aralığı ve kilitler |
| **Kullanıcı Ayarları**| `~/.config/pars/pars-update/settings.ini` | Kullanıcı tercihleri (otomatik başlatma, bildirimler, kontrol sıklığı) |
| **Hariç Tutulanlar**| `~/.config/pars/pars-update/user_keeps` | Kullanıcının güncellemek istemediği paketlerin listesi |
