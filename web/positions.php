<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SENAI Indústria 4.0 — Posições & Testes UR3 📍</title>
  <link rel="stylesheet" href="style.css">
  <style>
    .quick-actions-bar {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 1rem 1.25rem;
      margin-bottom: 1.5rem;
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      align-items: center;
      justify-content: space-between;
    }

    .action-group {
      display: flex;
      flex-wrap: wrap;
      gap: 0.6rem;
      align-items: center;
    }

    .paste-box {
      display: flex;
      gap: 0.5rem;
      align-items: center;
      background: rgba(0, 0, 0, 0.3);
      padding: 0.4rem 0.75rem;
      border-radius: 10px;
      border: 1px solid var(--border-color);
    }

    .paste-box input {
      background: transparent;
      border: none;
      color: #fff;
      font-family: var(--font-mono);
      font-size: 0.85rem;
      width: 280px;
      outline: none;
    }

    .positions-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
      gap: 1.25rem;
    }

    .pos-card {
      background: rgba(18, 26, 43, 0.7);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
      transition: border-color 0.2s ease, transform 0.2s ease;
    }

    .pos-card:hover {
      border-color: rgba(0, 212, 255, 0.4);
      transform: translateY(-2px);
    }

    .pos-card.special-card {
      background: linear-gradient(145deg, rgba(0, 212, 255, 0.06), rgba(18, 26, 43, 0.85));
      border-color: rgba(0, 212, 255, 0.3);
    }

    .pos-card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      padding-bottom: 0.6rem;
    }

    .pos-card-title {
      font-weight: 700;
      font-size: 1.05rem;
      color: var(--color-player);
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .pos-card-subtitle {
      font-size: 0.75rem;
      color: var(--color-text-muted);
    }

    .joints-inputs-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0.6rem;
    }

    .joint-field {
      display: flex;
      flex-direction: column;
      gap: 0.2rem;
    }

    .joint-field label {
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--color-text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .joint-field input {
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 8px;
      color: #fff;
      font-family: var(--font-mono);
      font-size: 0.9rem;
      padding: 0.4rem 0.5rem;
      text-align: right;
      width: 100%;
      box-sizing: border-box;
      transition: border-color 0.2s;
    }

    .joint-field input:focus {
      border-color: var(--color-player);
      outline: none;
      background: rgba(0, 212, 255, 0.05);
    }

    .radians-preview {
      font-family: var(--font-mono);
      font-size: 0.72rem;
      color: rgba(255, 255, 255, 0.4);
      background: rgba(0, 0, 0, 0.2);
      padding: 0.4rem 0.6rem;
      border-radius: 6px;
      line-height: 1.4;
      word-break: break-all;
    }

    .pos-card-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
      margin-top: 0.2rem;
    }

    .btn-sm {
      padding: 0.35rem 0.65rem;
      font-size: 0.78rem;
      border-radius: 8px;
      font-weight: 600;
    }

    .btn-outline {
      background: transparent;
      border: 1px solid var(--border-color);
      color: var(--color-text);
    }

    .btn-outline:hover {
      background: rgba(255, 255, 255, 0.08);
      border-color: #fff;
    }

    .btn-action-move {
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid var(--color-success);
      color: var(--color-success);
    }

    .btn-action-move:hover {
      background: var(--color-success);
      color: #000;
    }

    /* Modal de URScript */
    .modal-overlay {
      position: fixed;
      top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0, 0, 0, 0.8);
      backdrop-filter: blur(8px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }

    .modal-overlay.active {
      display: flex;
    }

    .modal-content {
      background: #0d131f;
      border: 1px solid var(--border-color);
      border-radius: 16px;
      width: 90%;
      max-width: 650px;
      max-height: 85vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }

    .modal-header {
      padding: 1rem 1.25rem;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .modal-header h3 {
      margin: 0;
      font-size: 1.1rem;
      color: var(--color-player);
    }

    .modal-body {
      padding: 1rem;
      overflow-y: auto;
      flex: 1;
    }

    .code-block {
      background: #05070a;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      padding: 0.85rem;
      font-family: var(--font-mono);
      font-size: 0.82rem;
      color: #00e5ff;
      white-space: pre-wrap;
      word-break: break-all;
    }

    .modal-footer {
      padding: 0.75rem 1.25rem;
      border-top: 1px solid var(--border-color);
      display: flex;
      justify-content: flex-end;
      gap: 0.5rem;
    }
  </style>
</head>
<body>

  <header>
    <div class="logo-container">
      <div class="senai-logo-badge">
        <svg width="105" height="30" viewBox="0 0 105 30" fill="none" xmlns="http://www.w3.org/2000/svg">
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
        <h1>SENAI — Configuração de Posições & Testes do Robô</h1>
        <p class="header-subtitle">Ajuste dos 6 ângulos de articulação (°), movimentos individuais e testes OnRobot</p>
      </div>
    </div>
    <div style="display: flex; gap: 0.75rem; align-items: center;">
      <a href="index.php" class="btn btn-outline btn-sm" style="text-decoration: none;">🎮 Jogar</a>
      <a href="calibrate.php" class="btn btn-outline btn-sm" style="text-decoration: none;">📷 Calibração</a>
      <div class="status-badge">
        <div id="statusDot" class="status-dot offline"></div>
        <span id="statusLabel">Offline</span>
      </div>
    </div>
  </header>

  <main style="display: block;">

    <!-- Barra de Ações Rápidas -->
    <div class="quick-actions-bar">
      <div class="action-group">
        <button class="btn btn-primary btn-sm" onclick="testAction('home')">
          🏠 Mover para HOME
        </button>
        <button class="btn btn-outline btn-sm" onclick="testAction('gripper_open')">
          ✋ Abrir Garra
        </button>
        <button class="btn btn-outline btn-sm" onclick="testAction('gripper_close')">
          ✊ Fechar Garra
        </button>
        <button class="btn btn-action-move btn-sm" onclick="saveAllPositions()">
          💾 Salvar TODAS as Posições
        </button>
        <button class="btn btn-outline btn-sm" onclick="loadPositions()">
          🔄 Recarregar
        </button>
      </div>

      <!-- Quick Import / colar do Teach Pendant -->
      <div class="paste-box">
        <span style="font-size: 0.78rem; color: var(--color-text-muted);">📋 Colar Teach Pendant (°):</span>
        <input type="text" id="pasteInput" placeholder="-87.14 -88.12 103.93 -105.88 -89.81 -21.33">
        <select id="pasteTarget" style="background: rgba(255,255,255,0.1); border: 1px solid var(--border-color); color:#fff; font-size:0.75rem; border-radius:6px; padding:0.2rem 0.4rem;">
          <option value="home">HOME</option>
          <option value="pick">PICK</option>
          <option value="0">Célula 0</option>
          <option value="1">Célula 1</option>
          <option value="2">Célula 2</option>
          <option value="3">Célula 3</option>
          <option value="4">Célula 4</option>
          <option value="5">Célula 5</option>
          <option value="6">Célula 6</option>
          <option value="7">Célula 7</option>
          <option value="8">Célula 8</option>
        </select>
        <button class="btn btn-primary btn-sm" style="padding: 0.25rem 0.5rem;" onclick="applyPastedDegrees()">Aplicar</button>
      </div>
    </div>

    <!-- Grid de Posições (Home, Pick, Células 0-8) -->
    <div class="positions-grid" id="positionsGrid">
      
      <!-- Card HOME -->
      <div class="pos-card special-card" id="card-home">
        <div class="pos-card-header">
          <div>
            <div class="pos-card-title">🏠 HOME POSE</div>
            <div class="pos-card-subtitle">Posição inicial segura do robô UR3</div>
          </div>
        </div>
        <div class="joints-inputs-grid">
          <div class="joint-field"><label>Base (°)</label><input type="number" step="0.01" id="home_j0" oninput="updateRadPreview('home')"></div>
          <div class="joint-field"><label>Ombro (°)</label><input type="number" step="0.01" id="home_j1" oninput="updateRadPreview('home')"></div>
          <div class="joint-field"><label>Cotovelo (°)</label><input type="number" step="0.01" id="home_j2" oninput="updateRadPreview('home')"></div>
          <div class="joint-field"><label>Pulso 1 (°)</label><input type="number" step="0.01" id="home_j3" oninput="updateRadPreview('home')"></div>
          <div class="joint-field"><label>Pulso 2 (°)</label><input type="number" step="0.01" id="home_j4" oninput="updateRadPreview('home')"></div>
          <div class="joint-field"><label>Pulso 3 (°)</label><input type="number" step="0.01" id="home_j5" oninput="updateRadPreview('home')"></div>
        </div>
        <div class="radians-preview" id="home_rad">Radianos: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]</div>
        <div class="pos-card-actions">
          <button class="btn btn-primary btn-sm" onclick="savePosition('home')">💾 Salvar Home</button>
          <button class="btn btn-action-move btn-sm" onclick="testJointMove('home')">🎯 Mover Robô Aqui</button>
        </div>
      </div>

      <!-- Card PICK -->
      <div class="pos-card special-card" id="card-pick">
        <div class="pos-card-header">
          <div>
            <div class="pos-card-title">📦 PONTO DE CAPTURA (PICK)</div>
            <div class="pos-card-subtitle">Posição de retirada da peça no estoque</div>
          </div>
        </div>
        <div class="joints-inputs-grid">
          <div class="joint-field"><label>Base (°)</label><input type="number" step="0.01" id="pick_j0" oninput="updateRadPreview('pick')"></div>
          <div class="joint-field"><label>Ombro (°)</label><input type="number" step="0.01" id="pick_j1" oninput="updateRadPreview('pick')"></div>
          <div class="joint-field"><label>Cotovelo (°)</label><input type="number" step="0.01" id="pick_j2" oninput="updateRadPreview('pick')"></div>
          <div class="joint-field"><label>Pulso 1 (°)</label><input type="number" step="0.01" id="pick_j3" oninput="updateRadPreview('pick')"></div>
          <div class="joint-field"><label>Pulso 2 (°)</label><input type="number" step="0.01" id="pick_j4" oninput="updateRadPreview('pick')"></div>
          <div class="joint-field"><label>Pulso 3 (°)</label><input type="number" step="0.01" id="pick_j5" oninput="updateRadPreview('pick')"></div>
        </div>
        <div class="radians-preview" id="pick_rad">Radianos: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]</div>
        <div class="pos-card-actions">
          <button class="btn btn-primary btn-sm" onclick="savePosition('pick')">💾 Salvar Pick</button>
          <button class="btn btn-action-move btn-sm" onclick="testJointMove('pick')">🎯 Mover Robô Aqui</button>
        </div>
      </div>

      <!-- Células 0 a 8 -->
      <?php
      $labels = [
        0 => "Superior Esquerdo (0)",
        1 => "Superior Centro (1)",
        2 => "Superior Direito (2)",
        3 => "Meio Esquerdo (3)",
        4 => "Meio Centro (4)",
        5 => "Meio Direito (5)",
        6 => "Inferior Esquerdo (6)",
        7 => "Inferior Centro (7)",
        8 => "Inferior Direito (8)"
      ];
      for ($c = 0; $c < 9; $c++):
      ?>
      <div class="pos-card" id="card-cell-<?php echo $c; ?>">
        <div class="pos-card-header">
          <div>
            <div class="pos-card-title">📍 Célula <?php echo $c; ?></div>
            <div class="pos-card-subtitle"><?php echo $labels[$c]; ?></div>
          </div>
        </div>
        <div class="joints-inputs-grid">
          <div class="joint-field"><label>Base (°)</label><input type="number" step="0.01" id="cell<?php echo $c; ?>_j0" oninput="updateRadPreview(<?php echo $c; ?>)"></div>
          <div class="joint-field"><label>Ombro (°)</label><input type="number" step="0.01" id="cell<?php echo $c; ?>_j1" oninput="updateRadPreview(<?php echo $c; ?>)"></div>
          <div class="joint-field"><label>Cotovelo (°)</label><input type="number" step="0.01" id="cell<?php echo $c; ?>_j2" oninput="updateRadPreview(<?php echo $c; ?>)"></div>
          <div class="joint-field"><label>Pulso 1 (°)</label><input type="number" step="0.01" id="cell<?php echo $c; ?>_j3" oninput="updateRadPreview(<?php echo $c; ?>)"></div>
          <div class="joint-field"><label>Pulso 2 (°)</label><input type="number" step="0.01" id="cell<?php echo $c; ?>_j4" oninput="updateRadPreview(<?php echo $c; ?>)"></div>
          <div class="joint-field"><label>Pulso 3 (°)</label><input type="number" step="0.01" id="cell<?php echo $c; ?>_j5" oninput="updateRadPreview(<?php echo $c; ?>)"></div>
        </div>
        <div class="radians-preview" id="cell<?php echo $c; ?>_rad">Radianos: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]</div>
        <div class="pos-card-actions">
          <button class="btn btn-primary btn-sm" onclick="savePosition('<?php echo $c; ?>')">💾 Salvar</button>
          <button class="btn btn-action-move btn-sm" onclick="testJointMove('<?php echo $c; ?>')">🎯 Mover</button>
          <button class="btn btn-outline btn-sm" onclick="testCellMove(<?php echo $c; ?>)">🤖 Pick&Place</button>
          <button class="btn btn-outline btn-sm" onclick="viewDryRun(<?php echo $c; ?>)">📜 Script</button>
        </div>
      </div>
      <?php endfor; ?>

    </div>

    <!-- Console de Eventos -->
    <div style="margin-top: 1.5rem;">
      <div class="panel-title" style="font-size: 1rem; padding-bottom: 0.5rem;">Console de Status & Eventos</div>
      <div class="logs-container" id="logsBox" style="height: 140px;">
        <div class="log-entry">[SISTEMA] Painel de Posições e Testes inicializado.</div>
      </div>
    </div>

  </main>

  <!-- Modal URScript Preview -->
  <div class="modal-overlay" id="scriptModal">
    <div class="modal-content">
      <div class="modal-header">
        <h3 id="modalTitle">URScript — Simulação Dry-Run</h3>
        <button class="btn btn-outline btn-sm" onclick="closeModal()">✕</button>
      </div>
      <div class="modal-body">
        <pre class="code-block" id="scriptCode">Carregando script...</pre>
      </div>
      <div class="modal-footer">
        <button class="btn btn-outline btn-sm" onclick="copyScript()">📋 Copiar Script</button>
        <button class="btn btn-primary btn-sm" onclick="closeModal()">Fechar</button>
      </div>
    </div>
  </div>

  <footer>
    SENAI — Centro de Treinamento e Desenvolvimento da Indústria 4.0 • UR3 Universal Robots × OnRobot RG2 Gripper
  </footer>

  <script>
    let posDataCache = null;

    function getBackendUrl(endpoint) {
      return 'api.php?action=' + endpoint;
    }

    function addLog(msg, type = 'info') {
      const logsBox = document.getElementById('logsBox');
      const time = new Date().toLocaleTimeString();
      const entry = document.createElement('div');
      entry.className = `log-entry ${type}`;
      entry.textContent = `[${time}] ${msg}`;
      logsBox.appendChild(entry);
      logsBox.scrollTop = logsBox.scrollHeight;
    }

    function checkStatus() {
      fetch(getBackendUrl('state'))
        .then(res => res.json())
        .then(data => {
          const dot = document.getElementById('statusDot');
          const label = document.getElementById('statusLabel');
          if (data && data.status !== 'offline') {
            dot.className = 'status-dot online';
            label.textContent = 'Online (' + data.status + ')';
          } else {
            dot.className = 'status-dot offline';
            label.textContent = 'Offline';
          }
        })
        .catch(() => {
          document.getElementById('statusDot').className = 'status-dot offline';
          document.getElementById('statusLabel').textContent = 'Offline';
        });
    }

    function degToRad(deg) {
      return Number((deg * Math.PI / 180).toFixed(5));
    }

    function radToDeg(rad) {
      return Number((rad * 180 / Math.PI).toFixed(2));
    }

    function getJointsFromForm(targetKey) {
      const prefix = targetKey === 'home' ? 'home_' : (targetKey === 'pick' ? 'pick_' : `cell${targetKey}_`);
      const degs = [];
      for (let j = 0; j < 6; j++) {
        const val = parseFloat(document.getElementById(`${prefix}j${j}`).value) || 0;
        degs.push(val);
      }
      return degs;
    }

    function updateRadPreview(targetKey) {
      const degs = getJointsFromForm(targetKey);
      const rads = degs.map(degToRad);
      const radEl = document.getElementById(targetKey === 'home' ? 'home_rad' : (targetKey === 'pick' ? 'pick_rad' : `cell${targetKey}_rad`));
      if (radEl) {
        radEl.textContent = 'Radianos: [' + rads.join(', ') + ']';
      }
    }

    function populateForm(data) {
      posDataCache = data;
      // Home
      if (data.home && data.home.degrees) {
        data.home.degrees.forEach((d, j) => {
          document.getElementById(`home_j${j}`).value = d;
        });
        updateRadPreview('home');
      }
      // Pick
      if (data.pick && data.pick.degrees) {
        data.pick.degrees.forEach((d, j) => {
          document.getElementById(`pick_j${j}`).value = d;
        });
        updateRadPreview('pick');
      }
      // Cells
      if (data.cells) {
        Object.keys(data.cells).forEach(c => {
          if (data.cells[c].degrees) {
            data.cells[c].degrees.forEach((d, j) => {
              const input = document.getElementById(`cell${c}_j${j}`);
              if (input) input.value = d;
            });
            updateRadPreview(c);
          }
        });
      }
    }

    function loadPositions() {
      addLog('Carregando posições configuradas no servidor...', 'info');
      fetch(getBackendUrl('positions'))
        .then(res => res.json())
        .then(data => {
          if (data.error) {
            addLog(`Erro ao carregar posições: ${data.error}`, 'error');
          } else {
            populateForm(data);
            addLog('✓ Posições carregadas com sucesso!', 'success');
          }
        })
        .catch(err => addLog(`Falha na comunicação: ${err}`, 'error'));
    }

    function savePosition(targetKey) {
      const degs = getJointsFromForm(targetKey);
      addLog(`Salvando posição '${targetKey}' (${degs.join('°, ')}°)...`, 'info');

      fetch(getBackendUrl('positions'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target: String(targetKey), degrees: degs })
      })
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          addLog(`❌ Erro ao salvar '${targetKey}': ${data.error}`, 'error');
        } else {
          addLog(`✓ Posição '${targetKey}' salva com sucesso no robô!`, 'success');
          loadPositions();
        }
      })
      .catch(err => addLog(`❌ Erro de conexão ao salvar: ${err}`, 'error'));
    }

    function saveAllPositions() {
      const allData = {
        home: { degrees: getJointsFromForm('home') },
        pick: { degrees: getJointsFromForm('pick') },
        cells: {}
      };
      for (let c = 0; c < 9; c++) {
        allData.cells[c] = { degrees: getJointsFromForm(c) };
      }

      addLog('Salvando TODAS as posições no servidor...', 'info');
      fetch(getBackendUrl('positions'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ all_positions: allData })
      })
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          addLog(`❌ Erro ao salvar posições em lote: ${data.error}`, 'error');
        } else {
          addLog('✓ TODAS as posições foram salvas com sucesso!', 'success');
          loadPositions();
        }
      })
      .catch(err => addLog(`❌ Erro ao enviar posições: ${err}`, 'error'));
    }

    function testAction(actionName) {
      addLog(`Enviando comando de teste: ${actionName}...`, 'info');
      fetch(getBackendUrl('test'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: actionName })
      })
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          addLog(`❌ Erro no teste: ${data.error}`, 'error');
        } else {
          addLog(`✓ ${data.message || 'Comando executado com sucesso!'}`, data.status === 'simulated' ? 'warn' : 'success');
        }
      })
      .catch(err => addLog(`❌ Falha na requisição de teste: ${err}`, 'error'));
    }

    function testJointMove(targetKey) {
      const degs = getJointsFromForm(targetKey);
      addLog(`Enviando robô para articulações de '${targetKey}' (${degs.join('° ')}°)...`, 'info');

      fetch(getBackendUrl('test'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'move_joint', target: String(targetKey), degrees: degs })
      })
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          addLog(`❌ Erro na movimentação: ${data.error}`, 'error');
        } else {
          addLog(`✓ ${data.message}`, data.status === 'simulated' ? 'warn' : 'success');
        }
      })
      .catch(err => addLog(`❌ Falha na conexão de teste: ${err}`, 'error'));
    }

    function testCellMove(cellIndex) {
      addLog(`Iniciando teste completo de Pick & Place para Célula ${cellIndex}...`, 'info');
      fetch(getBackendUrl('test'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'move_cell', cell: cellIndex })
      })
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          addLog(`❌ Erro no teste Pick & Place: ${data.error}`, 'error');
        } else {
          addLog(`✓ ${data.message}`, data.status === 'simulated' ? 'warn' : 'success');
        }
      })
      .catch(err => addLog(`❌ Erro de comunicação: ${err}`, 'error'));
    }

    function viewDryRun(cellIndex) {
      addLog(`Gerando script URScript Dry-Run para Célula ${cellIndex}...`, 'info');
      fetch(getBackendUrl('test'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'dry_run', cell: cellIndex })
      })
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          addLog(`❌ Erro ao gerar URScript: ${data.error}`, 'error');
        } else {
          document.getElementById('modalTitle').textContent = `URScript — Célula ${cellIndex} (Dry-Run)`;
          document.getElementById('scriptCode').textContent = data.script || 'Nenhum script gerado.';
          document.getElementById('scriptModal').className = 'modal-overlay active';
          addLog(`✓ URScript gerado para Célula ${cellIndex}. Exibindo janela...`, 'success');
        }
      })
      .catch(err => addLog(`❌ Falha na requisição: ${err}`, 'error'));
    }

    function closeModal() {
      document.getElementById('scriptModal').className = 'modal-overlay';
    }

    function copyScript() {
      const code = document.getElementById('scriptCode').textContent;
      navigator.clipboard.writeText(code).then(() => {
        addLog('📋 URScript copiado para a área de transferência!', 'success');
      });
    }

    function applyPastedDegrees() {
      const raw = document.getElementById('pasteInput').value.trim();
      const targetKey = document.getElementById('pasteTarget').value;
      if (!raw) return;

      const clean = raw.replace(/,/g, '.').replace(/;/g, ' ');
      const parts = clean.split(/\s+/).filter(Boolean);
      if (parts.length !== 6) {
        addLog(`❌ Entrada deve conter exatamente 6 números em graus (fornecidos ${parts.length}).`, 'error');
        return;
      }

      const prefix = targetKey === 'home' ? 'home_' : (targetKey === 'pick' ? 'pick_' : `cell${targetKey}_`);
      parts.forEach((p, j) => {
        const val = parseFloat(p);
        if (!isNaN(val)) {
          document.getElementById(`${prefix}j${j}`).value = val;
        }
      });
      updateRadPreview(targetKey);
      addLog(`✓ 6 valores colados e aplicados à posição '${targetKey}'!`, 'success');
    }

    // Inicialização
    loadPositions();
    checkStatus();
    setInterval(checkStatus, 3000);
  </script>
</body>
</html>
