#!/bin/bash
# =============================================================================
# start.sh — Inicia o sistema UR3 Jogo da Velha manualmente (Sem Node-RED)
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "================================================="
echo "  UR3 Jogo da Velha — Iniciando Sistema (Python+PHP)"
echo "================================================="

# Inicia o PHP Built-in Server em background na porta 8000
echo "Iniciando servidor Web PHP (Porta 8000)..."
cd "$PROJECT_DIR"
php -S 0.0.0.0:8000 -t web/ > /dev/null 2>&1 &
PHP_PID=$!

# Função para garantir encerramento do PHP quando der Ctrl+C no Python
cleanup() {
    echo ""
    echo "Encerrando servidor Web PHP (PID: $PHP_PID)..."
    kill $PHP_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "✓ Servidor PHP iniciado."
echo "✓ Dashboard disponível em: http://$(hostname -I | awk '{print $1}'):8000"
echo ""

# Ativa ambiente virtual e inicia o orquestrador Python + API
source venv/bin/activate
echo "Iniciando orquestrador Python e API Flask..."
python main.py
