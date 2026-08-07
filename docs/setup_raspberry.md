# Guia de Instalação e Configuração no Raspberry Pi 3B+

Este documento descreve detalhadamente o passo a passo para configurar o sistema no **Raspberry Pi 3B+** e como mapear as coordenadas físicas do robô **UR3**.

---

## 1. Preparação do Hardware e Rede

### Topologia de Rede
* O Raspberry Pi se conecta ao UR3 via **Cabo Ethernet (porta eth0)**.
* O Raspberry Pi se conecta à rede local via **Wi-Fi (wlan0)** para expor o Dashboard.

### Configurar IP Estático na eth0 do Raspberry Pi
Para conversar diretamente com o robô, a placa Ethernet do Raspberry Pi precisa ter um IP estático na mesma sub-rede do robô:

1. Abra o arquivo de configuração de rede no Raspberry Pi:
   ```bash
   sudo nano /etc/dhcpcd.conf
   ```
2. Adicione as seguintes linhas no final do arquivo:
   ```text
   interface eth0
   static ip_address=192.168.1.10/24
   static routers=192.168.1.1
   ```
3. Salve o arquivo (`Ctrl+O`, `Enter`) e saia (`Ctrl+X`).
4. Reinicie o serviço de rede para aplicar as alterações:
   ```bash
   sudo systemctl restart dhcpcd
   ```

### Configurar Rede no UR3 (Teach Pendant)
No painel do robô UR3 (Teach Pendant):
1. Vá em **Setup ➔ System ➔ Network**.
2. Configure o IP do robô:
   * **IP Address:** `192.168.1.100`
   * **Subnet Mask:** `255.255.255.0`
   * **Gateway:** `192.168.1.1`
3. Clique em **Apply** e valide a conectividade pingando o UR3 a partir do Raspberry Pi:
   ```bash
   ping 192.168.1.100
   ```

---

## 2. Instalação do Software no Raspberry Pi

O script automatizado [setup_raspberry.sh](file:///c:/Users/PC/OneDrive/Documentos/PROJETOS/Nova%20pasta/ur3_tictactoe/scripts/setup_raspberry.sh) realiza todo o processo de setup.

1. Baixe o projeto clonando o repositório público do GitHub e acesse a pasta:
   ```bash
   git clone https://github.com/3damatta/UR_JOGO_DA_VELHA.git
   cd UR_JOGO_DA_VELHA
   ```
2. Dê permissão de execução ao script:
   ```bash
   chmod +x scripts/setup_raspberry.sh
   ```
3. Execute o script com privilégios de superusuário:
   ```bash
   sudo bash scripts/setup_raspberry.sh
   ```

O script instalará o PHP, criará o ambiente virtual Python, baixará as dependências necessárias (Flask, OpenCV, PyYAML, Numpy) e registrará o serviço no `systemd` para iniciar no boot do sistema.

---

## 3. Calibração Física das Coordenadas do UR3

As coordenadas cartesianas das 9 posições do tabuleiro e do estoque devem ser informadas no arquivo [positions_config.json](file:///c:/Users/PC/OneDrive/Documentos/PROJETOS/Nova%20pasta/ur3_tictactoe/ur3/positions_config.json).

### Passo a passo para obter as coordenadas:

1. **Ativar Movimentação Manual (Free Drive):**
   * Pressione o botão traseiro do Teach Pendant para liberar as articulações do UR3 e mova o cabeçote manualmente.
2. **Posição HOME:**
   * Coloque o robô em uma posição elevada e centralizada que não obstrua o campo de visão da câmera sobre o tabuleiro.
   * Na aba **Move** do Teach Pendant, vá na aba **Joint** e anote os ângulos das 6 juntas.
   * Substitua a lista `joint_angles` dentro da seção `"home_pose"` em [positions_config.json](file:///c:/Users/PC/OneDrive/Documentos/PROJETOS/Nova%20pasta/ur3_tictactoe/ur3/positions_config.json).
3. **Posição de PICK (Estoque):**
   * Leve a garra até o local físico onde as peças laranjas do robô ficarão armazenadas (estoque/stack).
   * Desça a garra de forma linear (eixo Z) até tocar a peça. Garanta que o centro das garras coincida com o meio da peça.
   * Na aba **Move**, selecione a visualização **Pose** do TCP.
   * Anote os valores de `X, Y, Z` (em metros) e `Rx, Ry, Rz` (em radianos) exibidos.
   * Insira esses valores na chave `"pick"` no arquivo JSON.
4. **Posições do TABULEIRO (Células 0 a 8):**
   * Defina a altura padrão de inserção de peça. Encoste a garra com a peça levemente no tabuleiro e anote o valor do eixo `Z`. Este será o seu `"z_place"` (no formato numérico, ex: `0.110` metros).
   * Obtenha a orientação padrão de descida (normalmente vertical, ex: `Rx: 3.14159, Ry: 0.0, Rz: 0.0`). Substitua o array `"orientation"` no arquivo JSON.
   * Agora, mova o robô apenas nos eixos **X** e **Y** para o centro exato de cada uma das 9 células do tabuleiro físico (indexadas de 0 a 8).
   * Anote o `X` e `Y` de cada célula e insira nas respectivas chaves da seção `"cells"` dentro de `"board"` no JSON.

Exemplo de estrutura a ser editada no `positions_config.json`:
```json
  "home_pose": {
    "joint_angles": [-1.5708, -1.5708, -1.5708, -1.5708, 1.5708, 0.0]
  },
  "pick": {
    "x": 0.450, "y": -0.150, "z": 0.130,
    "rx": 3.14159, "ry": 0.0, "rz": 0.0
  },
  "board": {
    "z_place": 0.110,
    "orientation": [3.14159, 0.0, 0.0],
    "cells": {
      "0": {"x": 0.250, "y": 0.150, "label": "superior esquerdo"},
      "1": {"x": 0.350, "y": 0.150, "label": "superior centro"},
      ...
    }
  }
```

---

## 4. Testando Movimentos Individuais (Dry-Run)

Antes de rodar o sistema integrado, faça testes de movimentação isolados para garantir que não haja colisões:

* **Teste de Home:**
  ```bash
  python ur3/robot_controller.py
  ```
  *(O robô deve ir lentamente até a pose HOME configurada).*

* **Teste de Pick and Place simulado (Dry-Run):**
  Para imprimir na tela o script URScript gerado para uma célula (ex: célula 4) sem enviar ao robô físico:
  ```bash
  python ur3/robot_controller.py --cell 4 --dry-run
  ```

* **Teste de Movimento Real para Célula específica:**
  Mantenha a mão no botão de **Parada de Emergência (E-Stop)** do robô e execute o movimento real para a célula 4:
  ```bash
  python ur3/robot_controller.py --cell 4
  ```
