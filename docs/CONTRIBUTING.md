# Pars Update - Katkı Sağlama Kılavuzu (CONTRIBUTING.md)

Pars Update projesine katkıda bulunmak istediğiniz için teşekkür ederiz! Açık kaynak topluluğunun desteği, projenin gelişimi ve kararlılığı için çok değerlidir.

---

## 1. Katkıda Bulunma Yolları
* **Hata Bildirimi (Bug Reports):** Karşılaştığınız sorunları ve hata çıktılarını net adımlarla bildirin.
* **Yeni Özellik Önerileri (Feature Requests):** Dağıtım deneyimini geliştirecek önerilerinizi paylaşın.
* **Kod Katkıları (Pull Requests):** Hata düzeltmeleri, performans iyileştirmeleri ve yeni özellikler geliştirin.
* **Çeviriler (Translations):** Uygulamanın farklı dillerde kullanılabilmesi için `po/` dizinindeki çevirileri zenginleştirin.

---

## 2. Geliştirme İş Akışı

1. Depoyu forklayın veya yeni bir çalışma dalı (branch) oluşturun:
   ```bash
   git checkout -b feature/yeni-ozellik
   ```
2. Kod değişikliklerinizi yapın ve Python standartlarına (PEP 8) özen gösterin.
3. Sözdizimi ve derleme hatalarını kontrol edin:
   ```bash
   python3 -m py_compile src/*.py pars-update setup.py
   ```
4. Yeni metinler eklediyseniz çeviri şablonlarını güncelleyin:
   ```bash
   bash update-translations.sh
   ```
5. Değişikliklerinizi anlamlı commit mesajları ile kaydedin:
   ```bash
   git commit -m "feat(ui): güncelleme onay penceresine yeni ikon eklendi"
   ```
6. Dalınızı gönderin ve bir Pull Request (PR) açın.

---

## 3. Kodlama ve Güvenlik Kuralları

> [!CAUTION]
> Pars Update, sistem paketlerini ve kaynak listelerini yönettiği için güvenlik en öncelikli konudur.

* **Yetki Ayrımı:** GUI sürecine (`Main.py`, `MainWindow.py`) kesinlikle doğrudan root yetkisi verilmemeli; tüm ayrıcalıklı işlemler `SysActions.py` veya `AptSourceActions.py` üzerinden çağrılmalıdır.
* **Komut Enjeksiyonu Önleme:** `subprocess` çağrılarında `shell=True` kullanımından kaçının; argümanları liste (`list`) olarak iletin.
* **Girdi Doğrulama:** Root ile çalışan betiklere aktarılan tüm paket adları ve parametreler (`parse_packages`, `is_safe_sources`) doğrulanmalıdır.
* **Çoklu Dil Desteği:** Kullanıcıya görünen tüm dizgeler `_("Metin")` formatında gettext ile işaretlenmelidir.
