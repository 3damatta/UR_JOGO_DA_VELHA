#!/bin/bash
# =============================================================================
# setup_raspberry.sh — Configuração completa do Raspberry Pi 3B+
# UR3 Jogo da Velha (Sem Node-RED / Sem MQTT)
#
# TOPOLOGIA DE REDE:
#   Raspberry Pi eth0 ──(cabo)──▶ UR3 (192.168.1.100)
#   Raspberry Pi eth0 IP: 192.168.1.10 (estático)
#   Wi-Fi (wlan0): rede local para acesso ao dashboard (porta 8000)
#
# USO:
#   chmod +x scripts/setup_raspberry.sh
#   sudo bash scripts/setup_raspberry.sh
# =============================================================================

set -e  # Para em caso de erro

echo "================================================="
echo "  UR3 Jogo da Velha — Setup Raspberry Pi (Sem Node-RED)"
echo "================================================="

# ── 1. Atualizar sistema ──────────────────────────────────────────────────────
echo ""
echo "[1/5] Atualizando pacotes do sistema..."
apt-get update -qq
apt-get upgrade -y -qq

# ── 2. Instalar dependências do sistema ───────────────────────────────────────
echo ""
echo "[2/5] Instalando dependências (Python + OpenCV + PHP)..."
apt-get install -y -qq \
    python3 python3-pip python3-venv \
    libopencv-dev python3-opencv \
    php-cli \
    git curl wget \
    libatlas-base-dev \
    v4l-utils \
    cmake libboost-all-dev

# ── 3. Configurar rede estática eth0 ─────────────────────────────────────────
echo ""
echo "[3/5] Gerando arquivo de IP estático para eth0 (192.168.1.10)..."
cat > /etc/dhcpcd.conf.ur3 << 'EOF'
# Adicione estas linhas ao /etc/dhcpcd.conf para IP estático na eth0
# (conexão direta com o UR3)

interface eth0
static ip_address=192.168.1.10/24
static routers=192.168.1.1
# Sem DNS necessário para link direto com o UR3
EOF

echo "  ✓ Arquivo de configuração de rede gerado em /etc/dhcpcd.conf.ur3"
echo "  ⚠ ATENÇÃO: Adicione o conteúdo de /etc/dhcpcd.conf.ur3 ao /etc/dhcpcd.conf"
echo "  Execute: sudo cat /etc/dhcpcd.conf.ur3 >> /etc/dhcpcd.conf"
echo "  Depois reinicie: sudo systemctl restart dhcpcd"

# ── 4. Instalar dependências Python ──────────────────────────────────────────
echo ""
echo "[4/5] Configurando ambiente virtual Python e dependências..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
deactivate

echo "  ✓ Ambiente virtual configurado com Flask, OpenCV e PyYAML."

# ── 5. Criar serviço systemd ──────────────────────────────────────────────────
echo ""
echo "[5/5] Criando serviço systemd ur3-tictactoe..."
cat > /etc/systemd/system/ur3-tictactoe.service << EOF
[Unit]
Description=UR3 Jogo da Velha - Servidor de Jogo e Web PHP
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$PROJECT_DIR
ExecStart=/bin/bash $PROJECT_DIR/scripts/start.sh
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
Environment=PYTHONUNBUFFERED=1
Environment=DISPLAY=:0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ur3-tictactoe
echo "  ✓ Serviço ur3-tictactoe registrado com sucesso!"

# ── Resumo Final ──────────────────────────────────────────────────────────────
echo ""
echo "================================================="
echo "  SETUP CONCLUÍDO!"
echo "================================================="
echo ""
echo "  PRÓXIMOS PASSOS:"
echo "  1. Ative o IP estático da eth0:"
echo "     sudo cat /etc/dhcpcd.conf.ur3 >> /etc/dhcpcd.conf"
echo "     sudo systemctl restart dhcpcd"
echo ""
echo "  2. Configure o IP do UR3 para 192.168.1.100"
echo ""
echo "  3. Faça a calibração da câmera:"
echo "     cd $PROJECT_DIR"
echo "     source venv/bin/activate"
echo "     python vision/board_calibration.py"
echo ""
echo "  4. Inicie o jogo e a interface web:"
echo "     sudo systemctl start ur3-tictactoe"
echo ""
echo "  5. Acesse o Dashboard no navegador:"
echo "     http://$(hostname -I | awk '{print $1}'):8000"
echo "================================================="
