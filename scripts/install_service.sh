#!/bin/bash
# =============================================================================
# install_service.sh — Configura a inicialização automática do UR3 Jogo da Velha
# no boot do Raspberry Pi via systemd (100% autônomo, sem teclado/monitor/SSH)
# =============================================================================

set -e

if [ "$EUID" -ne 0 ]; then
    echo "❌ Erro: Execute este script com permissões de administrador (sudo):"
    echo "   sudo bash scripts/install_service.sh"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
USER_NAME="pi"

# Descobre o usuário dono da pasta caso não seja 'pi'
if [ -d "$PROJECT_DIR" ]; then
    FOUND_USER=$(stat -c '%U' "$PROJECT_DIR" 2>/dev/null || echo "pi")
    if [ "$FOUND_USER" != "root" ] && [ -n "$FOUND_USER" ]; then
        USER_NAME="$FOUND_USER"
    fi
fi

SERVICE_FILE="/etc/systemd/system/ur3-tictactoe.service"

echo "================================================="
echo "  UR3 Jogo da Velha — Instalador de Autostart"
echo "================================================="
echo "  Pasta do Projeto : $PROJECT_DIR"
echo "  Usuário          : $USER_NAME"
echo ""

# Criar o arquivo de serviço systemd
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=UR3 Jogo da Velha - Servidor de Jogo e Web Dashboard
After=network-online.target dhcpcd.service NetworkManager.service
Wants=network-online.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$PROJECT_DIR
ExecStart=/bin/bash $PROJECT_DIR/scripts/start.sh
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
Environment=PYTHONUNBUFFERED=1
Environment=DISPLAY=:0

[Install]
WantedBy=multi-user.target
EOF

chmod 644 "$SERVICE_FILE"

echo "✓ Serviço criado em: $SERVICE_FILE"

# Recarregar daemon do systemd e habilitar no boot
systemctl daemon-reload
systemctl enable ur3-tictactoe.service

# Iniciar o serviço imediatamente
systemctl restart ur3-tictactoe.service

echo ""
echo "================================================="
echo "  ✓ AUTOSERVIÇO CONFIGURADO E INICIADO COM SUCESSO!"
echo "================================================="
echo "  O sistema agora irá iniciar SOZINHO sempre que o Raspberry Pi for ligado."
echo ""
echo "  Comandos para gerenciar o serviço:"
echo "    • Ver status:         sudo systemctl status ur3-tictactoe"
echo "    • Reiniciar serviço:   sudo systemctl restart ur3-tictactoe"
echo "    • Parar serviço:       sudo systemctl stop ur3-tictactoe"
echo "    • Ver logs ao vivo:    sudo journalctl -u ur3-tictactoe -f"
echo "================================================="
