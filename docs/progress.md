# Pars Update - İlerleme ve Yol Haritası (progress.md)

Bu belge, **Pars Update (`pars-update`)** projesinde tamamlanan kilometre taşlarını, mevcut durumu ve gelecek geliştirme hedeflerini özetler.

---

## 1. Tamamlanan Kilometre Taşları (Completed)

- [x] **Çekirdek Sistem Entegrasyonu:** `python3-apt` tabanlı paket sorgulama ve önbellek yönetimi.
- [x] **Kullanıcı Arayüzü:** GTK+ 3 ve Glade ile modern pencere düzeni ve VTE terminal entegrasyonu.
- [x] **Sistem Tepsisi & Bildirimler:** Ayatana AppIndicator ve libnotify masaüstü bildirimleri.
- [x] **Güvenli Çevrimdışı Güncelleme:** Systemd `system-update.target` ve Plymouth açılış ekranı entegrasyonu.
- [x] **Yetki Ayrımı:** Polkit JavaScript kuralları (`.rules`) ve `pars-update` grubu ile parolasız kullanım.
- [x] **Seçilebilir Güncellemeler:** Kullanıcının güncellenecek paketleri tek tek seçebilmesi.
- [x] **Pars Update Rebranding:** Kod tabanının Pars Update (pars-update) olarak tam uyarlanması.

---

## 2. Mevcut Durum (Current Status - v0.7.1)
* Uygulama kararlı ve üretime hazır durumdadır.
* Tüm dokümantasyon (`docs/`) zenginleştirildi ve geliştiriciler için kılavuzlar hazırlandı.

---

## 3. Gelecek Yol Haritası (Future Roadmap)

### Kısa Vadeli Hedefler (v0.8.0)
- [ ] **NetworkManager Entegrasyonu:** Mobil / kotalı ağ tespit edildiğinde otomatik indirmeyi duraklatma.
- [ ] **Çekirdek (Kernel) Güncelleme Tespiti:** Sistem yeniden başlatma gerektiren çekirdek güncellemelerinde uyarı rozeti gösterme.
- [ ] **Wayland İyileştirmeleri:** Saf Wayland oturumlarında tepsi simgesi ve pencere yerleşimi uyumluluğunu artırma.

### Uzun Vadeli Hedefler (v1.0.0+)
- [ ] **GTK4 & Libadwaita:** Gelecek nesil masaüstleri için modern GTK4 portu.
- [ ] **Flatpak & Snap Desteği:** Sistem paketlerinin yanı sıra kurulu sandbox uygulamalarının güncellemelerini de tek ekranda listeleme.
- [ ] **Otomatik Güncelleme Zamanlayıcı:** Kullanıcının belirlediği saatlerde (ör. gece saatlerinde) otomatik sessiz indirme.
