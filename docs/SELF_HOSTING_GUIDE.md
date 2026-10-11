# Pars Update - Özel Depo ve Kendi Sunucunu Barındırma Kılavuzu (SELF_HOSTING_GUIDE.md)

Bu kılavuz, kurumsal ağlarda veya özel Pars Linux türevlerinde **Pars Update** ile uyumlu özel APT paket deposu ve sürüm kontrol uç noktası (`dists.json`) kurma adımlarını açıklar.

---

## 1. Özel APT Deposu Kurulumu (reprepro veya aptly)

Debian tabanlı sistemler için `reprepro` kullanarak yerel bir paket deposu oluşturabilirsiniz:

```bash
sudo apt install -y reprepro nginx gnupg
```

### 1.1 GPG Anahtarı Oluşturma
```bash
gpg --gen-key
# Anahtar ID'nizi öğrenin:
gpg --list-keys
```

### 1.2 Depo Yapılandırması (`conf/distributions`)
```
Origin: Pars Linux
Label: Pars
Codename: pars-bir
Architectures: amd64 i386
Components: main contrib non-free
SignWith: <GPG_KEY_ID>
```

### 1.3 Paketi Depoya Ekleme
```bash
reprepro -b /var/www/depo/ includedeb pars-bir /tmp/build/pars-update_*.deb
```

---

## 2. Dağıtım Sürüm Yükseltme Uç Noktası (`dists.json`)

Pars Update, yeni bir dağıtım sürümü (Distribution Upgrade) çıkıp çıkmadığını kontrol etmek için HTTP üzerinden bir JSON dosyası sorgular (`RepoDistControl.py`).

Kendi sunucunuzda `/dists.json` uç noktasını aşağıdaki formatta barındırabilirsiniz:

```json
{
  "repo": {
    "pars": [
      {
        "name": "yirmiuc",
        "version": 23,
        "status": "stable",
        "sources": "deb http://depo.pars.org.tr/pars yirmiuc main contrib non-free\n#deb-src http://depo.pars.org.tr/pars yirmiuc main contrib non-free\n"
      },
      {
        "name": "yirmibes",
        "version": 25,
        "status": "stable",
        "sources": "deb http://depo.pars.org.tr/pars yirmibes main contrib non-free\n#deb-src http://depo.pars.org.tr/pars yirmibes main contrib non-free\n"
      }
    ]
  }
}
```

### Parametre Açıklamaları:
* `version`: Dağıtımın tamsayı sürüm numarası (`/etc/os-release` içindeki `VERSION_ID`).
* `status`: `"stable"` veya `"testing"`. Pars Update yalnızca `"stable"` olanları otomatik yükseltme olarak sunar.
* `sources`: Yükseltme sırasında `/etc/apt/sources.list` dosyasına yazılacak yeni depo adresleri.

---

## 3. İstemcide Özel Depoyu Yapılandırma

İstemci bilgisayarlarda Pars Update'in yerel deponuzu varsayılan kaynak olarak tanıması için:
* `data/sources.json` dosyasını özel deponuzun adresleriyle güncelleyin ve paketi dağıtın.
* İstemciye deponuzun GPG genel anahtarını ekleyin:
  ```bash
  sudo wget -O /etc/apt/trusted.gpg.d/ozel-depo.gpg http://depo.alanadiniz.com/public.key
  ```
