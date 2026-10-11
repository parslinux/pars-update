#!/usr/bin/env bash
# ==============================================================================
# Pars Update (pars-update) - Kaldırma Betiği (uninstall.sh)
# ==============================================================================

set -e

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${RED}====================================================${NC}"
echo -e "${RED}         Pars Update Kaldırma Betiği                ${NC}"
echo -e "${RED}====================================================${NC}"

# Root kontrolü
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[Hata] Kaldırma işlemi için yönetici (root/sudo) yetkisi gereklidir.${NC}"
    echo -e "Lütfen betiği sudo ile çalıştırın: ${YELLOW}sudo ./uninstall.sh${NC}"
    exit 1
fi

# Onay isteme
PURGE=false
FORCE=false

for arg in "$@"; do
    case "$arg" in
        -y|--yes|--force)
            FORCE=true
            ;;
        --purge)
            PURGE=true
            ;;
    esac
done

if [ "$FORCE" = false ]; then
    read -p "Pars Update sistemden tamamen kaldırılsın mı? (e/H): " confirm
    if [[ ! "$confirm" =~ ^[eEyY]$ ]]; then
        echo -e "${YELLOW}Kaldırma işlemi iptal edildi.${NC}"
        exit 0
    fi
fi

echo -e "\n${YELLOW}[1/4] Uygulama dosyaları ve ikilileri siliniyor...${NC}"
rm -f /usr/bin/pars-update
rm -rf /usr/share/pars/pars-update/

echo -e "${YELLOW}[2/4] Masaüstü, simge ve çeviri dosyaları siliniyor...${NC}"
rm -f /usr/share/applications/org.pars.update.desktop
rm -f /etc/skel/.config/autostart/org.pars.update-autostart.desktop
rm -f /usr/share/icons/hicolor/scalable/apps/pars-update*.svg
find /usr/share/locale/ -name "pars-update.mo" -type f -delete 2>/dev/null || true

echo -e "${YELLOW}[3/4] Polkit ve servis yapılandırmaları temizleniyor...${NC}"
rm -f /usr/share/polkit-1/actions/org.pars.pkexec.pars-update.policy
rm -f /usr/share/polkit-1/rules.d/pars-update-group.rules
rm -f /usr/lib/systemd/system/pars-safeupgrade.service
rm -f /usr/lib/systemd/system/system-update.target.wants/pars-safeupgrade.service

# Konfigürasyon temizliği
if [ "$PURGE" = true ]; then
    echo -e "${YELLOW}Yapılandırma dosyaları siliniyor (/etc/pars/pars-update.conf)...${NC}"
    rm -f /etc/pars/pars-update.conf
    rmdir /etc/pars 2>/dev/null || true
fi

echo -e "${YELLOW}[4/4] Sistem önbellekleri yenileniyor...${NC}"
which update-desktop-database >/dev/null 2>&1 && update-desktop-database || true
which gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
systemctl restart polkit >/dev/null 2>&1 || true

echo -e "\n${GREEN}====================================================${NC}"
echo -e "${GREEN}      Pars Update Sistemden Başarıyla Kaldırıldı.   ${NC}"
echo -e "${GREEN}====================================================${NC}\n"
