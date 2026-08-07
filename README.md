# UR3 Jogo da Velha 🤖 × 🎮

Sistema integrado onde um robô Universal Robots UR3 joga Jogo da Velha contra um humano, usando visão computacional (OpenCV), um orquestrador central em Python (Flask) e um Dashboard Web em PHP.

> [!NOTE]
> Esta versão foi simplificada e otimizada, economizando significativamente os recursos de CPU e memória do Raspberry Pi 3B+.

---

## Arquitetura de Rede

```
┌─────────────────────────────────────────────────────────┐
│                    RASPBERRY PI 3B+                     │
│                                                         │
│     ┌─────────────────────┐     ┌─────────────────┐     │
│     │    PHP Web Server   │     │   Python Game   │     │
│     │      Port :8000     │◀───▶│   Server (Flask)│     │
│     │  (web/index.php UI) │     │   Port :5000    │     │
│     └─────────────────────┘     └────────┬────────┘     │
│                                          │              │
│                                          │ TCP :30002   │
│     ┌─────────────────────┐              │              │
│     │    OpenCV Thread    │──────────────┘              │
│     │     (detector.py)   │                             │
│     └──────────▲──────────┘                             │
│  eth0: 192.168.1.10                                     │
└──────────────┼───────────────────────────┼──────────────┘
               │ USB                       │ Cabo Ethernet
          ┌────┴────┐               ┌──────▼──────┐
          │ Câmera  │               │    UR3      │
          │   USB   │               │ 192.168.1.10│
          └─────────┘               │ OnRobot RG2 │
                                    └─────────────┘
```

---

## Estrutura de Arquivos

```
ur3_tictactoe/
├── main.py                          # Orquestrador central, API Flask e motor do jogo
├── requirements.txt                 # Dependências Python (Flask, OpenCV, PyYAML, etc.)
├── config/
│   ├── settings.yaml                # Configuração central (IPs, portas, câmera, HSV)
│   └── calibration.json             # Gerado pela calibração da câmera
├── vision/
│   ├── board_calibration.py         # Calibração do tabuleiro (executar 1x)
│   └── detector.py                  # Detecção em tempo real (X azul / O laranja) com callback
├── game/
│   └── minimax.py                   # IA Minimax com poda Alpha-Beta (Python)
├── ur3/
│   ├── robot_controller.py          # Geração de URScript + envio TCP (Primary Interface)
│   └── positions_config.json        # Coordenadas das 9 células (ajustar fisicamente!)
├── web/
│   ├── index.php                    # Dashboard visual principal (HTML/JS)
│   ├── api.php                      # Proxy API (comunica PHP -> Python)
│   └── style.css                    # Design System Premium (Glassmorphism, Dark Mode)
└── scripts/
    ├── setup_raspberry.sh           # Script de instalação do RPi (Instala PHP, venv, cria Systemd)
    └── start.sh                     # Script de inicialização unificado (PHP + Python)
```

---

## Instalação no Raspberry Pi 3B+

### Passo 1 — Configurar IP Estático (eth0)

No Raspberry Pi, edite o arquivo de rede:
```bash
sudo nano /etc/dhcpcd.conf
```
Adicione ao final do arquivo:
```text
interface eth0
static ip_address=192.168.1.10/24
```
Salve e reinicie o serviço de rede:
```bash
sudo systemctl restart dhcpcd
```

### Passo 2 — Configurar Rede do UR3

No Teach Pendant do UR3, configure:
* **IP Address:** `192.168.1.100`
* **Subnet Mask:** `255.255.255.0`
* **Gateway:** `192.168.1.1`

Valide a conexão executando no Raspberry Pi:
```bash
ping 192.168.1.100
```

### Passo 3 — Baixar o Projeto e Executar o Setup no Pi

Acesse o terminal do seu Raspberry Pi e execute os seguintes comandos para clonar o repositório público do GitHub e iniciar o instalador:

```bash
git clone https://github.com/3damatta/UR_JOGO_DA_VELHA.git
cd UR_JOGO_DA_VELHA
chmod +x scripts/setup_raspberry.sh
sudo bash scripts/setup_raspberry.sh
```
O script instalará:
* PHP (CLI)
* OpenCV e dependências do sistema
* Ambiente virtual Python e pacotes do `requirements.txt`
* Registro do serviço de segundo plano `ur3-tictactoe.service`

---

## Calibração da Câmera

Antes de iniciar a partida, a câmera USB deve ser calibrada sobre o tabuleiro físico.

```bash
source venv/bin/activate
python vision/board_calibration.py
```
**Instruções na Tela:**
1. Clique nos quatro cantos do tabuleiro (Superior-Esquerdo ➔ Superior-Direito ➔ Inferior-Direito ➔ Inferior-Esquerdo).
2. Valide se a grade desenhada se alinha com as células reais.
3. Pressione a tecla `S` para salvar as configurações de calibração em `config/calibration.json`.

---

## Iniciando o Jogo

### Modo Manual (Para Desenvolvimento/Testes)
```bash
bash scripts/start.sh
```
Isso iniciará o servidor PHP na porta `8000` e a API Flask na porta `5000`.

### Modo de Produção (Serviço do Sistema)
```bash
sudo systemctl start ur3-tictactoe
```

### Acessar a Interface
Abra qualquer navegador na mesma rede Wi-Fi e acesse:
```text
http://<IP_DO_RASPBERRY>:8000
```

---

## Fluxo da Partida

1. O jogador abre a interface web e clica em **Iniciar Jogo** (o robô vai para a pose HOME).
2. O jogador coloca sua peça **Azul (X)** no tabuleiro físico.
3. O detector de visão valida a peça por 8 frames estáveis.
4. O callback notifica o `GameManager` em Python.
5. O Python processa o tabuleiro, calcula a melhor jogada pelo `minimax.py` e muda o status para `robot_moving`.
6. O `GameManager` envia o URScript gerado ao UR3 via porta TCP `30002` e espera o robô concluir fisicamente.
7. O robô pega a peça **Laranja (O)** no estoque, coloca na célula escolhida e volta para a HOME.
8. O estado do jogo é atualizado na interface web em tempo real (polling).
9. O jogo encerra caso haja vitória ou empate.

---

## Troubleshooting (Solução de Problemas)

| Problema | Causa Provável | Solução |
| :--- | :--- | :--- |
| **Conexão Recusada ao UR3** | Robô desligado ou fora do modo Remoto. | Verifique se o TP do UR3 está configurado em modo remoto e o IP está correto. |
| **Câmera não abre** | Índice incorreto da câmera. | Altere o valor de `camera.index` no [settings.yaml](file:///c:/Users/PC/OneDrive/Documentos/PROJETOS/Nova%20pasta/ur3_tictactoe/config/settings.yaml). |
| **Dashboard exibe "Offline"** | Servidor Flask ou PHP inativo. | Execute `sudo systemctl status ur3-tictactoe` ou reinicie com `scripts/start.sh`. |
| **Peças não detectadas** | Iluminação ou valores de cor HSV incorretos. | Ajuste os valores de `detection.player_hsv` no [settings.yaml](file:///c:/Users/PC/OneDrive/Documentos/PROJETOS/Nova%20pasta/ur3_tictactoe/config/settings.yaml). |
