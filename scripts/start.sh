#!/bin/bash
# =============================================================================
# start.sh — Inicia o sistema UR3 Jogo da Velha manualmente (Sem Node-RED)
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "================================================="
echo "  UR3 Jogo da Velha — Iniciando Sistema (Python+PHP)"
echo "================================================="

# Garante encerramento de instâncias anteriores travadas nas portas 8000 ou 5000
pkill -f "php -S 0.0.0.0:8000" 2>/dev/null || true
pkill -f "python main.py" 2>/dev/null || true

# Inicia o PHP Built-in Server em background na porta 8000 (com múltiplos workers para evitar travamentos de stream)
echo "Iniciando servidor Web PHP com multiprocessamento (Porta 8000)..."
cd "$PROJECT_DIR"
export PHP_CLI_SERVER_WORKERS=4
php -S 0.0.0.0:8000 -t web/ > /dev/null 2>&1 &
PHP_PID=$!

# Função para garantir encerramento do PHP quando der Ctrl+C ou SIGTERM
cleanup() {
    echo ""
    echo "Encerrando servidor Web PHP (PID: $PHP_PID)..."
    kill $PHP_PID 2>/dev/null || true
    pkill -P $$ 2>/dev/null || true
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
