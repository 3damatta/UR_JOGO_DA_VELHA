# Guia de Operação e Calibração via SSH — UR3 Jogo da Velha 🤖×🎮

Este guia é um tutorial prático e direto para operar, calibrar e testar o sistema **UR3 Jogo da Velha** via **SSH através da rede Hotspot** do Raspberry Pi.

> [!NOTE]
> Este documento parte do pressuposto de que o sistema e todas as suas dependências já estão previamente instalados no Raspberry Pi.

---

## 📋 Sumário
0. [⚡ Inicialização Automática no Boot (Sem Teclado/Monitor/SSH)](#0--inicialização-automática-no-boot-sem-tecladomonitorssh)
1. [Conexão SSH via Hotspot](#1-conexão-ssh-via-hotspot)
2. [Passo 1 — Validação do IP do Robô UR3](#passo-1--validação-do-ip-do-robô-ur3)
3. [Passo 2 — Setup e Calibração da Câmera](#passo-2--setup-e-calibração-da-câmera)
4. [Passo 3 — Configuração dos Pontos de Rota (Posições do Robô)](#passo-3--configuração-dos-pontos-de-rota-posições-do-robô)
5. [Passo 4 — Comandos de Testes e Validação de Movimentos](#passo-4--comandos-de-testes-e-validação-de-movimentos)
6. [Passo 5 — Iniciando o Jogo e Acessando a Interface Web](#passo-5--iniciando-o-jogo-e-acessando-a-interface-web)

---

## 0. ⚡ Inicialização Automática no Boot (Sem Teclado/Monitor/SSH)

Para fazer com que todo o sistema (Hotspot + Servidor Python + Dashboard Web PHP) **inicie automaticamente ao ligar o Raspberry Pi na tomada**, execute este comando **uma única vez** via SSH:

```bash
sudo bash scripts/install_service.sh
```

> [!IMPORTANT]
> **Como Funciona:**
> - Ao energizar o Raspberry Pi, o serviço `ur3-tictactoe.service` roda sozinho em segundo plano via `systemd`.
> - O Wi-Fi Hotspot fica disponível e o Dashboard Web sobe na porta **8000**.
> - **Não é necessário monitor, teclado, mouse nem conexão SSH.** O operador só precisa ligar o Pi e abrir o navegador no smartphone/PC!
>
> **Comandos de Gerenciamento do Serviço (se necessário via SSH):**
> - **Ver status:** `sudo systemctl status ur3-tictactoe`
> - **Reiniciar:** `sudo systemctl restart ur3-tictactoe`
> - **Parar:** `sudo systemctl stop ur3-tictactoe`
> - **Logs ao vivo:** `sudo journalctl -u ur3-tictactoe -f`


---

## 1. Conexão SSH via Hotspot

1. No seu computador, notebook ou smartphone, conecte-se à rede Wi-Fi **Hotspot** emitida pelo Raspberry Pi.
2. Abra o terminal (PowerShell no Windows, Terminal no Linux/Mac) e acesse o Raspberry Pi via SSH:
   ```bash
   ssh pi@<IP_DO_HOTSPOT>
   ```
   *(Exemplo comum de IP do Hotspot: `ssh pi@192.168.4.1` ou `ssh pi@10.42.0.1`)*

3. Digite a senha do usuário `pi` para acessar o terminal.
4. Navegue até a pasta do projeto:
   ```bash
   cd ~/ur3_tictactoe
   ```

> [!TIP]
> **DICA 1 (Hotspot não inicia automático no boot?):**  
> Para fazer o Hotspot Wi-Fi ligar sozinho ao ligar o Raspberry Pi sem precisar de tela, execute este comando uma única vez no terminal do Pi:  
> `sudo nmcli connection modify "NOME_DO_HOTSPOT" connection.autoconnect yes connection.autoconnect-priority 10`

> [!TIP]
> **DICA 3 (Erro "ssh: connect to host ... port 22: Connection refused"?):**  
> Esse erro significa que a rede alcançou o Raspberry Pi, mas o serviço de SSH do sistema está desativado.  
> **Para ativar sem tela:** Retire o cartão MicroSD do Pi, coloque no computador, crie um arquivo em branco chamado **`ssh`** (sem extensão) dentro da unidade `boot` do cartão e recoloque no Pi. Ao ligar, o SSH será ativado automaticamente.

---

## Passo 1 — Validação do IP do Robô UR3

O Raspberry Pi comunica-se com o robô UR3 através da sua porta Ethernet (`eth0`).

### A) Verificação do IP no Robô UR3 (Teach Pendant)
1. No Teach Pendant do robô UR3, vá na tela superior em **Setup ➔ System ➔ Network**.
2. Garanta que as configurações estão definidas para:
   * **IP Address:** `192.168.1.100`
   * **Subnet Mask:** `255.255.255.0`
   * **Default Gateway:** `192.168.1.1`
3. Certifique-se de que o robô está no modo **Remote Control** (Modo Remoto).

### B) Validação da Comunicação no Terminal SSH
No terminal SSH do Raspberry Pi, valide a conexão enviando um ping ao robô:
```bash
ping 192.168.1.100
```
* **Resultado Esperado:** Respostas contínuas com o tempo de latência (`64 bytes from 192.168.1.100: icmp_seq=1 ttl=64 time=0.8 ms`).
* Pressione `Ctrl + C` para encerrar o ping.

---

## Passo 2 — Setup e Calibração da Câmera

A calibração mapeia a perspectiva da câmera sobre o tabuleiro físico de 3x3 posições.

### A) Calibração Interativa pela Interface Web (Recomendado — 0 Instalação no PC!)
Você pode calibrar a câmera diretamente pelo navegador do seu computador via Wi-Fi, sem precisar instalar programas no Windows ou conectar o Pi a um monitor:

1. Inicie o sistema via SSH no Raspberry Pi:
   ```bash
   bash scripts/start.sh
   ```
2. No seu computador conectado ao Wi-Fi Hotspot do Raspberry Pi, abra o navegador (Chrome/Edge) no endereço:
   ```text
   http://<IP_DO_HOTSPOT>:8000/calibrate.php
   ```
   *(Ou acesse `http://<IP_DO_HOTSPOT>:8000` e clique no botão **"📷 Calibrar Câmera"** no cabeçalho).*
3. Clique com o mouse na própria imagem da câmera exibida na tela do navegador para marcar os 4 cantos do tabuleiro na ordem:
   - **1º Clique:** Canto Superior-Esquerdo (SE) 🟢
   - **2º Clique:** Canto Superior-Direito (SD) 🟡
   - **3º Clique:** Canto Inferior-Direito (ID) 🔴
   - **4º Clique:** Canto Inferior-Esquerdo (IE) 🟣
4. Clique no botão **"💾 Salvar Calibração"**. A nova calibração será salva e aplicada automaticamente na memória do sistema!

---

### B) Método Alternativo via Terminal (Com Monitor conectado ao Pi)
Caso o Raspberry Pi esteja ligado a um monitor/TV físico com cabo HDMI e mouse no Pi:
```bash
source venv/bin/activate
DISPLAY=:0 python vision/board_calibration.py
```

### C) Ajustes de Parâmetros HSV ou Índice da Câmera (Opcional)
Caso seja necessário alterar o índice da câmera USB ou os limites de cores HSV (para a detecção das peças azuis e laranjas), edite o arquivo central via SSH:
```bash
nano config/settings.yaml
```
* Para salvar no nano: `Ctrl + O`, `Enter`. Para sair: `Ctrl + X`.

---

## Passo 3 — Configuração dos Pontos de Rota (Posições do Robô)

Todas as posições (HOME, Ponto de Captura e Células 0 a 8) podem ser configuradas online pela Dashboard Web ou via terminal SSH. Os valores das **6 articulações do robô são inseridos em GRAUS (°)**.

### A) Obter os Ângulos no Teach Pendant
1. No Teach Pendant do UR3, acesse a aba **Move ➔ Joint** (ou **Posições da Articulação**).
2. Você verá os 6 ângulos em graus referentes a:
   `Base`, `Ombro`, `Cotovelo`, `Pulso 1`, `Pulso 2` e `Pulso 3`.

### B) Configuração Online pela Dashboard Web (Recomendado — Sem Terminal!)
Você pode atualizar as posições e realizar testes de movimento diretamente pelo navegador:

1. No seu navegador, acesse a página de posições:
   ```text
   http://<IP_DO_HOTSPOT>:8000/positions.php
   ```
   *(Ou clique no botão **"📍 Posições & Testes"** no cabeçalho de qualquer página da Dashboard).*

2. **Como atualizar valores online:**
   * **Modo Direto:** Digite os 6 valores em graus (° com casas decimais) diretamente nos campos da posição desejada (HOME, PICK ou Células 0 a 8) e clique em **"💾 Salvar"**.
   * **Modo Copiar & Colar (Teach Pendant):** No topo da tela, cole a linha completa de 6 números lidos no Teach Pendant (ex: `-87.14 -88.12 103.93 -105.88 -89.81 -21.33`), selecione o alvo no menu suspenso e clique em **"Aplicar"**.
   * Para salvar todas as posições alteradas de uma só vez, clique em **"💾 Salvar TODAS as Posições"**.

3. **Botões de Teste Online de Posições e Movimentos:**
   * **"🎯 Mover Robô Aqui"**: Envia o robô diretamente para os 6 ângulos de articulação configurados (movej) para testar se a posição física no robô está precisa.
   * **"🤖 Pick & Place"**: Executa a sequência real completa de captura e posicionamento para aquela célula específica.
   * **"🏠 Mover para HOME"**: Retorna o braço do robô para a pose inicial de segurança com 1 clique.
   * **"✋ Abrir Garra" / "✊ Fechar Garra"**: Testa o acionamento da garra OnRobot online.
   * **"📜 Script"**: Abre uma janela com a simulação URScript (Dry-Run) gerada para aquela célula.

---

### C) Uso do Configurador via Terminal SSH (Alternativo)
Caso prefira usar o terminal SSH, execute:
```bash
python update_positions.py
```
O menu interativo permitirá visualizar (`V`), atualizar posições individuais (`H`, `P`, `0..8`) ou executar o assistente completo (`A`).

---

## Passo 4 — Comandos de Testes e Validação de Movimentos

Execute estes comandos via SSH para testar o robô e a garra antes de iniciar o jogo.

> [!WARNING]
> **SEGURANÇA:** Nos primeiros testes com movimento físico do robô, reduza a velocidade no Teach Pendant para **10%** ou **20%** e mantenha a mão sobre o botão de **Parada de Emergência (E-Stop)**.

### Teste 1: Acionamento da Garra OnRobot RG2/RG6
Testa a conexão XML-RPC com a garra na porta 41414 do robô:
```bash
python scripts/test_gripper.py
```
* **Comportamento Esperado:** A garra irá fechar para 38mm (força 20N), aguardar 3 segundos e abrir para 50mm.

### Teste 2: Teste de Simulação (Dry-Run / Sem mover o robô)
Gera o URScript de movimento para a célula 4 e exibe no terminal sem enviar ao robô físico:
```bash
python ur3/robot_controller.py --cell 4 --dry-run
```

### Teste 3: Movimento Físico para a Pose HOME
Envia o robô para a posição inicial de segurança:
```bash
python ur3/robot_controller.py
```
* **Comportamento Esperado:** O braço do robô moverá suavemente até a posição HOME configurada.

### Teste 4: Teste Real de Posicionamento para uma Célula (Ex: Célula 4)
Executa a sequência completa de pick & place (HOME ➔ PICK ➔ Garra Fecha ➔ Célula 4 ➔ Garra Abre ➔ HOME):
```bash
python ur3/robot_controller.py --cell 4
```

---

## Passo 5 — Iniciando o Jogo e Acessando a Interface Web

### A) Iniciar os Servidores via SSH
No terminal SSH do Raspberry Pi, rode o script de inicialização:
```bash
bash scripts/start.sh
```
*(Ou, se preferir rodar via serviço em segundo plano: `sudo systemctl start ur3-tictactoe`)*

### B) Acessar o Dashboard pelo Navegador
1. No seu dispositivo (notebook ou smartphone) conectado à rede Hotspot do Raspberry Pi, abra o navegador web.
2. Digite o endereço IP do Hotspot na porta **8000**:
   ```text
   http://<IP_DO_HOTSPOT>:8000
   ```
   *(Exemplo: `http://192.168.4.1:8000` ou `http://10.42.0.1:8000`)*

### C) Operação do Jogo
1. Clique em **"Iniciar Jogo"** na tela. O robô irá para a pose HOME.
2. O jogador coloca a peça azul (**X**) no tabuleiro.
3. O detector reconhece a jogada e aciona o turno do robô (**O** laranja).
4. O robô busca a peça no estoque e realiza o movimento físico no tabuleiro.
