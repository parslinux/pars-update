# Pars Update - Çeviri ve Yerelleştirme Kılavuzu (TRANSLATION_GUIDE.md)

Bu kılavuz, **Pars Update** uygulamasının yeni dillere çevrilmesi veya mevcut çevirilerin güncellenmesi sürecini açıklar.

---

## 1. Çeviri Altyapısı
Pars Update, standart GNU gettext altyapısını kullanır:
* **Kaynak Kod Dizgeleri:** `_("Metin")`
* **Kaynak Listesi:** `po/files` (çevrilebilir dizgelerin taranacağı kaynak dosyalar)
* **Şablon Dosyası:** `po/pars-update.pot`
* **Dil Dosyaları:** `po/<dil_kodu>.po` (ör. `po/tr.po`, `po/pt.po`)

---

## 2. Çeviri Şablonlarını Güncelleme

Kaynak kodda veya Glade arayüz dosyasında yeni bir metin eklendiğinde:

```bash
# update-translations.sh betiğini çalıştırın:
bash update-translations.sh
```
Bu betik:
1. `xgettext` ile `po/files` içindeki dosyalardan en güncel dizgeleri tarar ve `po/pars-update.pot` dosyasını oluşturur.
2. `msgmerge` kullanarak mevcut `.po` dosyalarını yeni şablonla birleştirir.

---

## 3. Yeni Bir Dil Ekleme

Örneğin Almanca (`de`) dil desteği eklemek için:

1. `update-translations.sh` dosyasındaki `langs` dizisine `"de"` ekleyin:
   ```bash
   langs=("tr" "pt" "de")
   ```
2. Şablon dosyasını kopyalayın:
   ```bash
   cp po/pars-update.pot po/de.po
   ```
3. `po/de.po` dosyasını **Poedit**, **Gtranslator** veya bir metin editörüyle açarak çevirileri tamamlayın.

---

## 4. Çevirileri Test Etme

Çevirileri yerel ortamda test etmek için:

```bash
# setup.py ile .mo ikili dosyalarını üretin:
python3 setup.py --name

# Uygulamayı hedef dilde çalıştırın:
LANGUAGE=pt_PT python3 src/Main.py
LANGUAGE=tr_TR python3 src/Main.py
```
