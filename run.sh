#!/usr/bin/env bash
# ==============================================================================
# Pars Update (pars-update) - Çalıştırma Betiği (run.sh)
# ==============================================================================

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Yardım menüsü
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo -e "${BLUE}Pars Update Çalıştırma Betiği${NC}"
    echo -e "Kullanım: ./run.sh [SEÇENEKLER]"
    echo -e ""
    echo -e "Seçenekler:"
    echo -e "  (parametre yok)         Ana pencereyi açar."
    echo -e "  --tray, -t              Sistem tepsisi (tray indicator) modunda başlatır."
    echo -e "  --page updateinfo       Doğrudan bekleyen güncellemeler sayfasını açar."
    echo -e "  --system                Kaynak kodu yerine kurulu /usr/bin/pars-update'i çalıştırır."
    echo -e "  -h, --help              Bu yardım iletisini gösterir."
    exit 0
fi

# Root uyarısı (GUI root olarak başlatılmamalı)
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}[Uyarı] Pars Update arayüzü doğrudan 'root' olarak çalıştırılmamalıdır.${NC}"
    echo -e "Güvenlik gereği lütfen normal kullanıcı hesabınızla çalıştırın."
fi

# Python bağımlılık kontrolü
python3 -c "import gi, distro, apt" >/dev/null 2>&1 || {
    echo -e "${RED}[Hata] Gerekli Python kütüphaneleri eksik görünüyor.${NC}"
    echo -e "Lütfen kurulum betiğini çalıştırın veya bağımlılıkları yükleyin:"
    echo -e "  ${YELLOW}sudo ./install.sh${NC}"
    echo -e "veya elle:"
    echo -e "  ${YELLOW}sudo apt install -y python3-apt python3-distro gir1.2-gtk-3.0 gir1.2-vte-2.91 gir1.2-ayatanaappindicator3-0.1${NC}"
    exit 1
}

# Sistemde kurulu olanı çalıştırma isteği
if [ "$1" == "--system" ]; then
    shift
    if [ -x "/usr/bin/pars-update" ]; then
        echo -e "${GREEN}Sistemdeki /usr/bin/pars-update çalıştırılıyor...${NC}"
        exec /usr/bin/pars-update "$@"
    else
        echo -e "${RED}[Hata] /usr/bin/pars-update bulunamadı. Lütfen önce './install.sh' çalıştırın.${NC}"
        exit 1
    fi
fi

# Kaynak koddan çalıştırma
echo -e "${GREEN}Pars Update kaynak dizininden başlatılıyor...${NC}"
exec python3 "$SCRIPT_DIR/src/Main.py" "$@"
