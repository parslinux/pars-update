# Pars Update - Sürüm Yönetimi ve Politikası (VERSION.md)

Bu belge, **Pars Update (`pars-update`)** projesinin sürümleme politikasını, sürüm numarasının nasıl belirlendiğini ve yeni sürüm çıkarma adımlarını açıklar.

---

## 1. Sürümleme Modeli (Semantic Versioning)

Pars Update, **SemVer 2.0.0** (`MAJOR.MINOR.PATCH`) standardını takip eder:
* **MAJOR (Ana Sürüm):** Geriye dönük uyumsuz köklü mimari veya arayüz değişikliklerinde (ör. Python 2'den 3'e geçiş, GTK3'ten GTK4'e geçiş).
* **MINOR (İkincil Sürüm):** Geriye dönük uyumlu yeni özellikler ve modüller eklendiğinde (ör. yeni temizlik modülü, çevrimdışı güncelleme entegrasyonu).
* **PATCH (Düzeltme Sürümü):** Geriye dönük uyumlu hata düzeltmeleri, güvenlik yamaları ve çeviri güncellemelerinde.

---

## 2. Sürümün Kod İçinde Belirlenmesi

Projede sürüm numarası **tek bir kaynaktan (Single Source of Truth)** yönetilir:
1. Kaynak dosya: [debian/changelog](file:///home/can/Masaüstü/projeler/mcsm/masaüstü/inceleme_düzenleme/upteda/debian/changelog)
2. [setup.py](file:///home/can/Masaüstü/projeler/mcsm/masaüstü/inceleme_düzenleme/upteda/setup.py), derleme sırasında `debian/changelog` dosyasının ilk satırını ayrıştırır (örneğin: `pars-update (0.7.1) ...` -> `0.7.1`).
3. Elde edilen sürüm `src/__version__` dosyasına yazılır ve `MainWindow.py` tarafından "Hakkında" penceresinde gösterilir.

---

## 3. Yeni Sürüm Çıkarma Adımları (Release Checklist)

1. **Changelog Güncellemesi:**
   `debian/changelog` dosyasının en üstüne yeni sürüm kaydını ekleyin:
   ```debian
   pars-update (0.7.2) unstable; urgency=medium

     * Yeni özellik veya hata düzeltme açıklaması

    -- Geliştirici Adı <email@alanadi.org>  Pzt, 12 Eki 2026 12:00:00 +0300
   ```
2. **Değişiklik Günlüğü:**
   [CHANGELOG.md](file:///home/can/Masaüstü/projeler/mcsm/masaüstü/inceleme_düzenleme/upteda/CHANGELOG.md) içerisine yeni sürüme ait özet maddeleri ekleyin.
3. **Çeviriler:**
   `bash update-translations.sh` çalıştırarak en güncel dizgeleri derleyin.
4. **Sözdizimi Kontrolü:**
   `python3 -m py_compile src/*.py pars-update setup.py` komutuyla hatasızlığı onaylayın.
5. **Git Etiketi:**
   ```bash
   git add .
   git commit -m "chore(release): v0.7.2"
   git tag -a v0.7.2 -m "Release v0.7.2"
   ```
