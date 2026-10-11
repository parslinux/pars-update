#!/usr/bin/env bash
# ==============================================================================
# Pars Update (pars-update) - Kurulum Betiği (install.sh)
# ==============================================================================

set -e

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}          Pars Update Kurulum Betiği                ${NC}"
echo -e "${BLUE}====================================================${NC}"

# Root / Sudo kontrolü
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[Hata] Kurulum için yönetici (root/sudo) yetkisi gereklidir.${NC}"
    echo -e "Lütfen betiği sudo ile çalıştırın: ${YELLOW}sudo ./install.sh${NC}"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Bağımlılıkların Kontrolü ve Yüklenmesi
echo -e "\n${YELLOW}[1/5] Gerekli sistem bağımlılıkları kontrol ediliyor...${NC}"
DEPENDENCIES=(
    "python3"
    "python3-apt"
    "python3-distro"
    "python3-setuptools"
    "gir1.2-glib-2.0"
    "gir1.2-gtk-3.0"
    "gir1.2-notify-0.7"
    "gir1.2-soup-2.4"
    "gir1.2-vte-2.91"
    "gir1.2-ayatanaappindicator3-0.1"
    "policykit-1"
    "gettext"
)

MISSING_DEPS=()
for dep in "${DEPENDENCIES[@]}"; do
    if ! dpkg -s "$dep" >/dev/null 2>&1; then
        MISSING_DEPS+=("$dep")
    fi
done

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${YELLOW}Eksik paketler tespit edildi: ${MISSING_DEPS[*]}${NC}"
    echo -e "Paketler apt ile yükleniyor..."
    apt-get update -qq
    apt-get install -y "${MISSING_DEPS[@]}"
else
    echo -e "${GREEN}Tüm bağımlılıklar sistemde mevcut.${NC}"
fi

# 2. Çeviri (.mo) Dosyalarının Derlenmesi
echo -e "\n${YELLOW}[2/5] Dil çeviri dosyaları derleniyor...${NC}"
if [ -f "update-translations.sh" ]; then
    bash update-translations.sh >/dev/null 2>&1 || true
fi

# 3. Dosyaların Sisteme Kurulması
echo -e "\n${YELLOW}[3/5] Pars Update dosyaları sisteme kopyalanıyor...${NC}"
python3 setup.py install --prefix=/usr --install-layout=deb >/dev/null 2>&1 || python3 setup.py install --prefix=/usr

# İkili dosya izinlerini sağlama
chmod +x /usr/bin/pars-update
chmod +x /usr/share/pars/pars-update/src/SysActions.py
chmod +x /usr/share/pars/pars-update/src/AptSourceActions.py
chmod +x /usr/share/pars/pars-update/src/AutoAptUpdate.py
chmod +x /usr/share/pars/pars-update/src/Group.py
chmod +x /usr/share/pars/pars-update/src/SystemSettingsWrite.py

# 4. Sistem Grubu ve Yetkilendirme Yapılandırması
echo -e "\n${YELLOW}[4/5] Polkit ve sistem grupları yapılandırılıyor...${NC}"
getent group pars-update >/dev/null 2>&1 || addgroup --system pars-update || true

# Betiği sudo ile çağıran gerçek kullanıcıyı gruba ekleme
REAL_USER="${SUDO_USER:-$USER}"
if [ "$REAL_USER" != "root" ] && [ -n "$REAL_USER" ]; then
    if ! id -nG "$REAL_USER" | grep -qw "pars-update"; then
        usermod -a -G pars-update "$REAL_USER" || adduser "$REAL_USER" pars-update || true
        echo -e "${GREEN}'$REAL_USER' kullanıcısı 'pars-update' grubuna eklendi (Parolasız güncelleme aktif).${NC}"
    fi
fi

# 5. Sistem Önbelleklerinin Yenilenmesi
echo -e "\n${YELLOW}[5/5] Masaüstü ve simge önbellekleri güncelleniyor...${NC}"
which update-desktop-database >/dev/null 2>&1 && update-desktop-database || true
which gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
systemctl restart polkit >/dev/null 2>&1 || true

echo -e "\n${GREEN}====================================================${NC}"
echo -e "${GREEN}      Pars Update Başarıyla Kuruldu! 🎉            ${NC}"
echo -e "${GREEN}====================================================${NC}"
echo -e "Uygulamayı başlatmak için:"
echo -e "  * Menüden: ${YELLOW}Uygulamalar -> Sistem -> Pars Güncelleyici${NC}"
echo -e "  * Terminalden: ${YELLOW}pars-update${NC}"
echo -e "  * Test betiğiyle: ${YELLOW}./run.sh${NC}"
echo -e "\nKaldırmak isterseniz: ${YELLOW}sudo ./uninstall.sh${NC}\n"
