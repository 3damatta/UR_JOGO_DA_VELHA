<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SENAI Indústria 4.0 — UR3 Jogo da Velha 🤖</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>

  <header>
    <div class="logo-container">
      <div class="senai-logo-badge">
        <svg width="105" height="30" viewBox="0 0 105 30" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- SENAI Vector Text -->
          <path d="M 19 6 H 6 V 14 H 19 V 23 H 6" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="square" stroke-linejoin="miter"/>
          <path d="M 26 6 H 37 M 26 14.5 H 35 M 26 23 H 37 M 26 6 V 23" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="square"/>
          <path d="M 44 23 V 6 L 57 23 V 6" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="square" stroke-linejoin="miter"/>
          <path d="M 64 23 L 71 6 L 78 23 M 66.5 17 H 75.5" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="square" stroke-linejoin="miter"/>
          <path d="M 85 6 V 23" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="square"/>
          <rect x="5" y="27" width="82" height="3" fill="#E30613" rx="1"/>
        </svg>
        <span class="i40-badge">INDÚSTRIA 4.0</span>
      </div>
      <div class="header-titles">
        <h1>SENAI — Célula de Robótica Colaborativa</h1>
        <p class="header-subtitle">Centro de Treinamento e Desenvolvimento da Indústria 4.0 • UR3 Jogo da Velha</p>
      </div>
    </div>
    <div class="status-badge">
      <div id="statusDot" class="status-dot offline"></div>
      <span id="statusLabel">Offline</span>
    </div>
  </header>

  <main>
    <!-- Painel da Câmera (Visão Computacional) -->
    <div class="panel">
      <div class="panel-title">
        <span>Visão da Câmera (Câmera USB)</span>
        <span style="font-size: 0.8rem; font-weight: normal; color: var(--color-text-muted);" id="camResolution">640x480 (HSV)</span>
      </div>
      <div class="camera-container">
        <!-- O source é atualizado dinamicamente via JS com o IP correto do backend -->
        <img id="cameraFeed" class="camera-feed" src="" alt="Aguardando feed da câmera...">
      </div>
      <div style="font-size: 0.85rem; color: var(--color-text-muted); line-height: 1.5;">
        <strong>Como Jogar:</strong> Coloque uma peça <strong>Azul (X)</strong> no tabuleiro físico dentro do campo de visão da câmera, ou clique diretamente nas células do tabuleiro virtual ao lado para jogar no modo manual.
      </div>
    </div>

    <!-- Painel de Controle e Tabuleiro -->
    <div class="panel">
      <div class="panel-title">Tabuleiro & Controles</div>
      
      <div class="board-wrapper">
        <div class="tictactoe-board" id="boardGrid">
          <!-- Células geradas dinamicamente via Javascript -->
          <?php for ($i = 0; $i < 9; $i++): ?>
            <div class="cell" data-index="<?php echo $i; ?>" onclick="makeMove(<?php echo $i; ?>)"></div>
          <?php endfor; ?>
        </div>
      </div>

      <div class="controls-panel">
        <div class="game-state-banner">
          <span class="state-label">Estado da Partida</span>
          <span class="state-value" id="gameStateLabel">Carregando...</span>
        </div>

        <div class="difficulty-selector">
          <label for="difficultySelect">Dificuldade do Robô:</label>
          <select id="difficultySelect" onchange="changeDifficulty(this.value)">
            <option value="easy">Fácil 🟢 (Vitória Humana Provável)</option>
            <option value="medium" selected>Médio 🟡 (Jogo Justo & Equilibrado)</option>
            <option value="impossible">MODO HERÓI ⚡ (Desafio Impossível)</option>
          </select>
        </div>

        <button class="btn btn-primary" onclick="resetGame()">
          <svg style="width:20px;height:20px" viewBox="0 0 24 24"><path fill="currentColor" d="M17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35Z" /></svg>
          Iniciar / Reiniciar Jogo
        </button>
      </div>

      <div class="panel-title" style="font-size: 1rem; border-top: 1px solid var(--border-color); padding-top: 1rem; margin-top: 0.5rem;">Console de Eventos</div>
      <div class="logs-container" id="logsBox">
        <div class="log-entry">[SISTEMA] Dashboard carregado.</div>
      </div>
    </div>
  </main>

  <footer>
    SENAI — Centro de Treinamento e Desenvolvimento da Indústria 4.0 • UR3 Universal Robots × OnRobot RG2 Gripper
  </footer>

  <script>
    let currentBoard = Array(9).fill('');
    let gameActive = false;
    let gameStatus = 'offline';
    let isPolling = true;

    // Configura a URL da câmera de acordo com o host atual
    document.getElementById('cameraFeed').src = `http://${window.location.hostname}:5000/api/stream`;

    // Função de Log Interno do Dashboard
    function logEvent(message, type = 'info') {
      const logsBox = document.getElementById('logsBox');
      const entry = document.createElement('div');
      entry.className = `log-entry ${type}`;
      
      const time = new Date().toLocaleTimeString();
      entry.innerText = `[${time}] ${message}`;
      
      logsBox.appendChild(entry);
      logsBox.scrollTop = logsBox.scrollHeight;
    }

    // Busca o Estado Atual do Jogo (Polling)
    async function fetchState() {
      if (!isPolling) return;
      try {
        const res = await fetch('api.php?action=state');
        if (!res.ok) throw new Error('Falha na resposta da API');
        const state = await res.json();
        
        updateUI(state);
      } catch (err) {
        updateOfflineUI();
      }
    }

    // Atualiza a Interface de acordo com o estado do backend
    function updateUI(state) {
      // Atualiza o Badge de Status da Conexão
      const statusDot = document.getElementById('statusDot');
      const statusLabel = document.getElementById('statusLabel');
      
      statusDot.className = 'status-dot online';
      statusLabel.innerText = 'Online';

      // Verifica se houve mudança no tabuleiro para logar
      for (let i = 0; i < 9; i++) {
        if (currentBoard[i] !== state.board[i]) {
          if (state.board[i] === 'X') {
            logEvent(`Peça 'X' detectada na célula ${i}`, 'success');
          } else if (state.board[i] === 'O') {
            logEvent(`Peça 'O' colocada pelo robô na célula ${i}`, 'warning');
          }
          currentBoard[i] = state.board[i];
        }
      }

      gameActive = state.game_active;
      gameStatus = state.status;

      // Renderiza as células no grid
      const cells = document.querySelectorAll('.cell');
      cells.forEach((cell, idx) => {
        const val = state.board[idx];
        cell.className = 'cell';
        cell.innerText = val;
        if (val === 'X') cell.classList.add('x');
        if (val === 'O') cell.classList.add('o');
        
        // Destaque da linha vencedora
        if (state.winning_line && state.winning_line.includes(idx)) {
          cell.classList.add('winner-cell');
        }
      });

      // Atualiza o banner de status
      const stateLabel = document.getElementById('gameStateLabel');
      const statusDotLabel = document.getElementById('statusDot');

      if (state.status === 'ongoing') {
        stateLabel.innerText = 'Jogo em Andamento. Aguardando Jogador...';
        stateLabel.style.color = 'var(--color-player)';
        statusDotLabel.className = 'status-dot online';
      } else if (state.status === 'robot_moving') {
        stateLabel.innerText = 'Robô calculando e jogando...';
        stateLabel.style.color = 'var(--color-robot)';
        statusDotLabel.className = 'status-dot busy';
      } else if (state.status === 'player_wins') {
        stateLabel.innerText = 'Você Venceu! 🎉';
        stateLabel.style.color = 'var(--color-success)';
      } else if (state.status === 'robot_wins') {
        stateLabel.innerText = 'O Robô Venceu! 🤖';
        stateLabel.style.color = 'var(--color-danger)';
      } else if (state.status === 'draw') {
        stateLabel.innerText = 'Deu Velha! Empate.';
        stateLabel.style.color = 'var(--color-text-muted)';
      } else {
        stateLabel.innerText = 'Jogo Pronto. Pressione "Iniciar / Reiniciar".';
        stateLabel.style.color = '#fff';
      }

      // Sincroniza o seletor de dificuldade com o estado do backend
      if (state.difficulty) {
        const diffSelect = document.getElementById('difficultySelect');
        if (diffSelect && diffSelect.value !== state.difficulty) {
          diffSelect.value = state.difficulty;
        }
      }
    }

    function updateOfflineUI() {
      const statusDot = document.getElementById('statusDot');
      const statusLabel = document.getElementById('statusLabel');
      statusDot.className = 'status-dot offline';
      statusLabel.innerText = 'Offline';

      const stateLabel = document.getElementById('gameStateLabel');
      stateLabel.innerText = 'Conexão perdida com o servidor Python.';
      stateLabel.style.color = 'var(--color-danger)';
    }

    // Altera a dificuldade da IA
    async function changeDifficulty(newDifficulty) {
      logEvent(`Alterando dificuldade para '${newDifficulty}'...`);
      try {
        isPolling = false;
        const res = await fetch(`api.php?action=difficulty&difficulty=${newDifficulty}`);
        const data = await res.json();
        isPolling = true;

        if (data.status === 'success') {
          const names = { 'easy': 'Fácil 🟢', 'medium': 'Médio 🟡', 'impossible': 'MODO HERÓI ⚡', 'hard': 'MODO HERÓI ⚡' };
          logEvent(`✓ Dificuldade alterada para: ${names[newDifficulty] || newDifficulty}`, 'info');
          updateUI(data.state);
        } else {
          logEvent('Erro ao alterar dificuldade.', 'error');
        }
      } catch (err) {
        logEvent('Erro de conexão ao alterar dificuldade.', 'error');
        isPolling = true;
      }
    }

    // Executa Jogada Manual ao Clicar na Célula
    async function makeMove(cellIdx) {
      if (gameStatus !== 'ongoing') {
        logEvent('Ação inválida: O jogo não está ativo ou o robô está movendo.', 'error');
        return;
      }
      if (currentBoard[cellIdx] !== '') {
        logEvent('Célula já ocupada!', 'error');
        return;
      }

      logEvent(`Tentativa de jogada manual na célula ${cellIdx}...`);
      try {
        isPolling = false; // pausa polling para evitar conflito de rede
        const res = await fetch(`api.php?action=move&cell=${cellIdx}`);
        const data = await res.json();
        isPolling = true;

        if (data.success) {
          updateUI(data.state);
        } else {
          logEvent('Jogada rejeitada pelo servidor.', 'error');
        }
      } catch (err) {
        logEvent('Erro ao enviar jogada.', 'error');
        isPolling = true;
      }
    }

    // Reinicia o Jogo
    async function resetGame() {
      logEvent('Solicitando reinicialização do jogo...');
      try {
        isPolling = false;
        const res = await fetch('api.php?action=reset');
        const data = await res.json();
        isPolling = true;

        if (data.status === 'success') {
          currentBoard = Array(9).fill('');
          logEvent('=== NOVO JOGO INICIADO ===', 'success');
          updateUI(data.state);
        } else {
          logEvent(`Falha ao reiniciar: ${data.error || 'Erro no backend'}`, 'error');
        }
      } catch (err) {
        logEvent('Erro de comunicação ao reiniciar jogo.', 'error');
        isPolling = true;
      }
    }

    // Inicia o Polling de Estado (500ms)
    setInterval(fetchState, 500);
    fetchState();
  </script>
</body>
</html>
