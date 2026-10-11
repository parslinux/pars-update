# Pars Update - Veri, Disk ve Bant Genişliği Tasarruf Kılavuzu (DATA_SAVING_GUIDE.md)

Bu kılavuz, **Pars Update** kullanarak hem disk alanından tasarruf etmeyi hem de kotalı veya mobil internet bağlantılarında veri tüketimini en aza indirme stratejilerini açıklar.

---

## 1. Disk Alanı Tasarrufu ve Temizlik Araçları

Pars Update, yerleşik bir paket ve önbellek temizleme paneline sahiptir (`Ayarlar > Paket Yöneticisi Önbelleği`):

### 1.1 İndirilen `.deb` Paketleri Önbelleği (`apt clean`)
* **Konum:** `/var/cache/apt/archives/`
* **İşlev:** Yüklenen paketlerin kurulum dosyaları diskte saklanır. Uzun süre temizlenmezse gigabaytlarca yer kaplayabilir.
* **Tasarruf:** Pars Update arayüzünden *"Önbellekteki deb paketleri"* seçeneği işaretlenip *"Temizle"* butonuna basılarak güvenle silinebilir.

### 1.2 Artık Yapılandırma Dosyaları (`Residual Packages`)
* **Durum:** Daha önce kaldırılmış ancak ayar dosyaları silinmemiş paketler (`dpkg` üzerinde `rc` durumu).
* **Tasarruf:** Pars Update, artık paketleri otomatik tespit eder ve `--purge` parametresiyle tamamen temizler.

### 1.3 Kullanılmayan Bağımlılıklar (`apt autoremove`)
* Bir uygulama kaldırıldığında onunla birlikte gelen kütüphaneler sistemde sahipsiz kalabilir.
* Pars Update, otomatik kaldırılabilir paketlerin toplam boyutunu hesaplayarak tek tıkla temizlemenizi sağlar.

---

## 2. İnternet Kotası ve Veri Tasarrufu Stratejileri

Mobil bağlantı veya sınırlı internet kotası kullanırken gereksiz veri tüketimini önlemek için:

### 2.1 Güncelleme Kontrol Sıklığını Değiştirme
* `Ayarlar > Güncelleme Kontrol Sıklığı` bölümünden sıklığı **"Haftalık"** veya **"Asla"** olarak ayarlayabilirsiniz.
* "Asla" seçildiğinde arka planda otomatik indirme yapılmaz; kontroller yalnızca siz istediğinizde tetiklenir.

### 2.2 Seçilebilir Güncellemeler (Selectable Updates)
* `Ayarlar > Seçilebilir Güncellemeler` anahtarını aktif hale getirin.
* Bu özellik sayesinde tüm güncellemeleri tek seferde indirmek yerine, yalnızca ihtiyaç duyduğunuz veya kritik güvenlik paketlerini seçerek veri harcamasını kontrol altında tutabilirsiniz.

### 2.3 APT Liste Önbelleğini Korumak
* APT her `update` yaptığında depo indekslerini indirir. Çok sık `apt update` çalıştırmamak mobil kota tasarrufu sağlar.
