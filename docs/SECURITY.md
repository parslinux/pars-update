# Pars Update - Güvenlik Politikası ve Mimarisi (SECURITY.md)

Bu belge, **Pars Update** uygulamasının güvenlik modelini, ayrıcalık sınırlarını ve güvenlik açıklarını bildirme sürecini açıklar.

---

## 1. Güvenlik Modeli ve İlkeleri

Pars Update, işletim sisteminin paket yöneticisiyle doğrudan etkileşime girdiği için en katı güvenlik standartlarına uygun olarak tasarlanmıştır:

### 1.1 En Az Ayrıcalık İlkesi (Principle of Least Privilege)
* Grafiksel arayüz (GUI) bileşenleri asla `root` yetkisiyle çalıştırılamaz.
* Yalnızca paket kurulumu, önbellek silme veya kaynak listesi düzenleme gibi ayrıcalık gerektiren eylemler `pkexec` üzerinden çağrılır.

### 1.2 Girdi Doğrulama ve Sanitizasyon (Input Validation)
* **Paket İsimleri:** `SysActions.py` içerisindeki `parse_packages` fonksiyonu, paket isimlerinin geçerli Debian paket adlandırma kurallarına (`^[a-z0-9][a-z0-9+.-]+$`) uyduğunu doğrular. Zararlı komut zincirleme (`&&`, `;`, `|`, `` ` ``) girişimleri engellenir.
* **Kaynak Listesi Filtresi:** `is_safe_sources` fonksiyonu; `trusted=yes`, `allow-insecure`, `file://` gibi güvensiz depo parametrelerinin `sources.list` içine eklenmesini engeller.

### 1.3 Polkit Yetkilendirme Kısıtlamaları
* Polkit politikaları (`org.pars.pkexec.pars-update.policy`), çalıştırılabilecek betiklerin mutlak yollarını (`/usr/share/pars/pars-update/src/...`) sabitler. Farklı dizinlerden bu politika ile komut çalıştırılamaz.

---

## 2. Güvenlik Açığı Bildirimi

Pars Update'te bir güvenlik açığı tespit ederseniz, lütfen bunu herkese açık GitHub Issue olarak bildirmek yerine:
* **E-posta:** `guvenlik@pars.org.tr` veya proje yöneticisine özel mesaj ile iletiniz.
* Bildirilen güvenlik açıkları öncelikli olarak incelenir ve düzeltme yaması yayınlanana kadar gizlilikle yönetilir.
