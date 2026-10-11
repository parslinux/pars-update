# Pars Update - Komut Satırı ve Betik Referansı (CLI_REFERENCE.md)

Bu belge, **Pars Update** ikili komutunu (`pars-update`) ve arka planda çalışan Python betiklerinin terminal parametrelerini listeler.

---

## 1. Ana Komut: `pars-update`

Masaüstü ve kullanıcı terminalinden çağrılan ana komut.

```bash
pars-update [SEÇENEKLER]
```

### Seçenekler:
* `-h, --help`: Yardım iletisini ve kullanılabilir parametreleri gösterir.
* `-t, --tray`: Uygulamayı ana pencereyi açmadan, yalnızca sistem tepsisi (tray indicator) modunda başlatır.
* `-p, --page <SAYFA>`: Uygulamayı doğrudan belirtilen sayfayı açarak başlatır.
  * Kullanılabilir sayfalar: `updateinfo` (güncellenecek paketler listesi), `ok` (sistem güncel sayfası), `settings` (ayarlar).

---

## 2. Ayrıcalıklı Eylem Betikleri (`src/`)

Bu betikler genellikle `MainWindow.py` tarafından `pkexec` aracılığıyla çağrılır.

### 2.1 `src/SysActions.py`
Sistem düzeyinde paket ve önbellek işlemlerini yürütür.

| Alt Komut | Parametreler | Açıklama |
| :--- | :--- | :--- |
| `upgrade` | `<yq_state>` `<dpkg_conf_state>` `[keeps]` | Paket yükseltmesini başlatır (`-yq` ve dpkg conf modları ile). |
| `removeresidual` | `<paket_listesi>` | Artık yapılandırması kalmış paketleri purge eder. |
| `removeauto` | - | Kullanılmayan bağımlılıkları temizler (`apt autoremove`). |
| `controldistupgrade`| `<sources_list>` | Dağıtım sürüm yükseltmesi için ön kontrol yapar. |
| `downupgrade` | `<sources_list>` | Yükseltme paketlerini önceden indirir. |
| `distupgradeoffline`| `<sources_list>` `<askconf>` | Çevrimdışı yükseltme servisini hazırlar ve yeniden başlatır. |
| `dpkgconfigure` | - | Yarıda kalan paket işlemlerini onarır (`dpkg --configure -a`). |
| `aptclear` | `<clean>` `<autoremove>` `<aptlists>` | APT önbellek dosyalarını temizler. |

### 2.2 `src/AptSourceActions.py`
Depo kaynak listesi düzenleme ve onarım eylemleri.

| Alt Komut | Parametreler | Açıklama |
| :--- | :--- | :--- |
| `setsourcestate` | `<state: 0\|1>` `<line>` `<file_path>` | Belirli bir depo satırını etkinleştirir veya devre dışı bırakır. |
| `fixsources` | `<slist>` `<fix_slistd>` `<remove>` `<conf>` `<fixbroken>` | Kaynak listesini varsayılanlara sıfırlar ve bağımlılıkları onarır. |

### 2.3 `src/Group.py`
Kullanıcı grubu yönetimi (`pars-update` grubu).

| Alt Komut | Parametre | Açıklama |
| :--- | :--- | :--- |
| `add` | `<kullanici_adi>` | Kullanıcıyı parolasız güncelleme grubuna ekler. |
| `del` | `<kullanici_adi>` | Kullanıcıyı parolasız güncelleme grubundan çıkarır. |

### 2.4 `src/SystemSettingsWrite.py`
Sistem genelindeki `/etc/pars/pars-update.conf` dosyasına güvenli yazma.

| Alt Komut | Parametreler | Açıklama |
| :--- | :--- | :--- |
| `write` | `lastupdate` `<timestamp>` | Son güncelleme zaman damgasını kaydeder. |
