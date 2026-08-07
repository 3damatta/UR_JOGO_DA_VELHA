# Protocolo de Testes e Validação Real

Este documento detalha os procedimentos de teste recomendados para validar cada componente do sistema antes e durante a operação real do Jogo da Velha com o robô UR3.

---

## 1. Testes de Visão Computacional e Câmera

### Teste 1.1: Validação da Homografia (Corte do Tabuleiro)
* **Objetivo:** Garantir que o tabuleiro físico está sendo mapeado perfeitamente para a imagem plana (normalizada) de 300x300 pixels.
* **Procedimento:**
  1. Execute a calibração com `python vision/board_calibration.py`.
  2. Selecione os 4 cantos do tabuleiro.
  3. Após salvar, abra a interface web em `http://localhost:8000`.
  4. Observe a miniatura no canto superior direito do feed de vídeo. Ela deve exibir apenas o tabuleiro, perfeitamente quadrado, plano e sem distorções de perspectiva.

### Teste 1.2: Sensibilidade e Filtro de Cores (HSV)
* **Objetivo:** Garantir que o sistema detecta as peças do jogador (X azul) e ignora variações de luz natural e sombras.
* **Procedimento:**
  1. Coloque uma peça azul na célula 4 (centro).
  2. Verifique na janela do terminal do `main.py` se o log exibe: `[VISION] INFO: ► Jogador colocou X na célula 4`.
  3. No painel visual da Web, a célula central correspondente deve exibir a letra **X** na cor azul-neon.
  4. Repita o teste acendendo e apagando as luzes da sala para garantir que o filtro HSV configurado em `settings.yaml` seja robusto. Se a peça sumir da detecção, refaça o ajuste dos limites HSV.

---

## 2. Testes de Integração e Servidores (API / Web)

### Teste 2.1: Comunicação Proxy (PHP ➔ Flask)
* **Objetivo:** Validar se a interface em PHP consegue ler o estado e disparar ações no backend em Python.
* **Procedimento:**
  1. Suba o sistema com `bash scripts/start.sh` ou ative o serviço do systemd.
  2. Acesse `http://localhost:8000`.
  3. O indicador de conexão no canto superior direito do cabeçalho deve exibir **"Online"** na cor verde.
  4. Clique no botão **"Iniciar / Reiniciar Jogo"** e verifique no console de logs do rodapé se a mensagem `=== NOVO JOGO INICIADO ===` é exibida instantaneamente.

### Teste 2.2: Transmissão de Vídeo (MJPEG Stream)
* **Objetivo:** Garantir a entrega fluida da imagem processada pelo OpenCV via protocolo HTTP.
* **Procedimento:**
  1. Na página do dashboard, mexa a mão na frente da câmera.
  2. O feed de vídeo no painel esquerdo deve atualizar com uma taxa estável de frames (~15 FPS) e baixíssima latência (menor que 100ms).

---

## 3. Testes da Inteligência Artificial (Minimax)

### Teste 3.1: IA Defensiva (Bloqueio)
* **Objetivo:** Validar se a lógica do Minimax em Python impede a vitória fácil do jogador.
* **Procedimento:**
  1. Inicie um novo jogo.
  2. Clique nas células **0** e **1** (Jogador joga X).
  3. O robô deve calcular e escolher obrigatoriamente a célula **2** para se defender e bloquear a linha.
  4. Valide se a interface mostra que o robô jogou na célula 2.

### Teste 3.2: IA Ofensiva (Vitória)
* **Objetivo:** Validar se a IA aproveita oportunidades para vencer a partida.
* **Procedimento:**
  1. Simule uma partida onde o robô (peça O) já possua marcações nas células **3** e **4**.
  2. Faça uma jogada qualquer irrelevante (ex: célula 0).
  3. O robô deve escolher a célula **5** para completar a linha horizontal média e vencer.
  4. A tela deve destacar a linha vencedora em roxo e exibir o banner: `O Robô Venceu! 🤖`.

---

## 4. Testes Físicos do Robô (Segurança e Colisão)

> [!WARNING]
> Mantenha sempre a mão sobre o botão físico de **Parada de Emergência (E-Stop)** no Teach Pendant do UR3 durante a realização destes testes!

### Teste 4.1: Dry-Run de Trajetória
* **Objetivo:** Garantir que o script gerado não atinge os limites de junta do robô nem se choca com a mesa.
* **Procedimento:**
  1. Coloque o robô no modo manual, posicione-o na HOME e reduza a velocidade geral do UR3 para **10%** no Teach Pendant.
  2. No terminal do Raspberry Pi, execute o teste de trajetória para a célula 0:
     ```bash
     python ur3/robot_controller.py --cell 0
     ```
  3. Observe atentamente a movimentação do braço robótico. Ele deve ir da HOME ➔ aproximar 50mm acima da peça ➔ descer lentamente ➔ fechar garra ➔ subir ➔ mover até 50mm acima da célula 0 ➔ descer ➔ abrir garra ➔ subir ➔ voltar para HOME.

### Teste 4.2: Teste da Garra OnRobot
* **Objetivo:** Validar se a abertura/fechamento das garras coincide com o tamanho físico das peças de jogo.
* **Procedimento:**
  1. Com o robô em modo manual e seguro, execute o fechamento de teste:
     ```bash
     python ur3/robot_controller.py --cell 4
     ```
  2. O robô irá realizar o ciclo completo. Verifique se o diâmetro configurado para pegar a peça (`close_width` no settings.yaml) aperta a peça firmemente sem escorregar e se a abertura (`open_width`) abre espaço suficiente para liberar a peça no tabuleiro sem arrastá-la.
