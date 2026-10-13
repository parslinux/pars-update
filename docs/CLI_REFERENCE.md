# Pars Update - Komut Satırı ve Betik Referansı (CLI_REFERENCE.md)

Bu belge, **Pars Update** ana komutunu (`pars-update`) ve arka planda çalışan Python modüllerinin terminal parametrelerini listeler.

---

## 1. Ana Komut: `pars-update`

Masaüstü ve kullanıcı terminalinden çağrılan ana komut.

```bash
pars-update [SEÇENEKLER]
```

### Seçenekler:
* `-h, --help`: Yardım iletisini ve kullanılabilir GApplication parametrelerini gösterir.
* `-t, --tray`: Uygulamayı ana pencereyi açmadan, arka plan / sistem tepsisi modunda başlatır.
* `-c, --check`: Arka planda depoları kontrol eder; ana pencereyi açmaz, yeni paket varsa masaüstü bildirimi gönderir.
* `-p, --page <SAYFA>`: Uygulamayı doğrudan belirtilen sayfayı açarak başlatır:
  * `updates` / `updateinfo`: Güncellenecek paketler listesi sayfası.
  * `settings` / `preferences`: Ayarlar ve sistem bakımı iletişim penceresi.
  * `uptodate` / `ok`: Sistem güncel sayfası.
  * `checking`: Güncelleme arama (spinner) sayfası.
  * `terminal`: Canlı VTE yükseltme konsolu.
  * `error`: Kilit / hata sayfası.
* `--gtk3`, `--legacy`: Modern GTK4 / Libadwaita yerine klasik GTK3 `MainWindow` arayüzünü zorlar.

---

## 2. Ayrıcalıklı Eylem Betikleri (`src/`)

Bu betikler genellikle `MainWindowAdw.py` veya `SysActions.py` tarafından `pkexec` aracılığıyla root yetkisiyle çağrılır.

### 2.1 `src/SysActions.py`
Sistem düzeyinde paket ve önbellek işlemlerini yürütür (Arch Linux Pacman ve Debian APT için çift motorlu).

| Alt Komut | Parametreler | Açıklama |
| :--- | :--- | :--- |
| `upgrade` | `<yq_state>` `<dpkg_conf_state>` `[keeps]` | Paket yükseltmesini başlatır (`pacman -Syu` veya `apt full-upgrade`). |
| `removeresidual` | `<paket_listesi>` | Artık yapılandırması kalmış paketleri purge eder. |
| `removeauto` | - | Kullanılmayan yetim bağımlılıkları temizler (`pacman -Rns $(pacman -Qdtq)` veya `apt autoremove`). |
| `controldistupgrade`| `<sources_list>` | Dağıtım sürüm yükseltmesi için ön kontrol yapar. |
| `downupgrade` | `<sources_list>` | Yükseltme paketlerini önceden indirir. |
| `distupgradeoffline`| `<sources_list>` `<askconf>` | Çevrimdışı yükseltme servisini hazırlar ve yeniden başlatır. |
| `dpkgconfigure` | - | Yarıda kalan işlemleri veya paket yöneticisi kilidini onarır (`pacman` sürecini denetleyip kilit siler veya `dpkg --configure -a`). |
| `aptclear` | `<clean>` `<autoremove>` `<aptlists>` | Paket arşiv önbelleğini temizler (`pacman -Sc` veya `apt clean`). |

### 2.2 `src/AptSourceActions.py`
Depo kaynak listesi düzenleme ve yansı yönetimi eylemleri.

| Alt Komut | Parametreler | Açıklama |
| :--- | :--- | :--- |
| `setsourcestate` | `<state: 0\|1>` `<line>` `<file_path>` | Belirli bir ayna (`mirrorlist`) veya depo satırını etkinleştirir/kapatır. |
| `fixsources` | `<slist>` `<fix_slistd>` `<remove>` `<conf>` `<fixbroken>` | Kaynak listesini varsayılanlara sıfırlar ve bağımlılıkları onarır. |

### 2.3 `src/Group.py`
Kullanıcı grubu yönetimi (`pars-update` grubu ile parolasız polkit kullanımı).

| Alt Komut | Parametre | Açıklama |
| :--- | :--- | :--- |
| `add` | `<kullanici_adi>` | Kullanıcıyı parolasız güncelleme grubuna ekler (`gpasswd`, `usermod`). |
| `del` | `<kullanici_adi>` | Kullanıcıyı parolasız güncelleme grubundan çıkarır. |

### 2.4 `src/SystemSettingsWrite.py`
Sistem genelindeki `/etc/pars/pars-update.conf` dosyasına güvenli yazma.

| Alt Komut | Parametreler | Açıklama |
| :--- | :--- | :--- |
| `write` | `<ayar_adi>` `<deger>` | Sistem genelinde güncelleme aralığı veya yapılandırma kaydeder. |
