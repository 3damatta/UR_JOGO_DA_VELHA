<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SENAI Indústria 4.0 — Calibração da Câmera 📷</title>
  <link rel="stylesheet" href="style.css">
  <style>
    .cal-instructions {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .step-item {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.6rem 0.85rem;
      border-radius: 10px;
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid transparent;
      font-size: 0.9rem;
      transition: all 0.2s ease;
    }

    .step-item.active {
      background: rgba(0, 212, 255, 0.1);
      border-color: var(--color-player);
      color: #fff;
    }

    .step-item.done {
      background: rgba(16, 185, 129, 0.1);
      border-color: var(--color-success);
      color: #fff;
    }

    .step-number {
      width: 26px;
      height: 26px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 0.8rem;
      background: rgba(255, 255, 255, 0.1);
      color: var(--color-text-muted);
    }

    .step-item.active .step-number {
      background: var(--color-player);
      color: #000;
    }

    .step-item.done .step-number {
      background: var(--color-success);
      color: #000;
    }

    /* Container Interativo da Câmera com Overlay */
    .interactive-camera-box {
      position: relative;
      width: 100%;
      background-color: #05070a;
      border-radius: 16px;
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.1);
      cursor: crosshair;
      user-select: none;
    }

    .interactive-camera-box img {
      width: 100%;
      height: auto;
      display: block;
    }

    .svg-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
    }

    .coords-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
    }

    .coords-table th, .coords-table td {
      padding: 0.5rem 0.75rem;
      text-align: left;
      border-bottom: 1px solid var(--border-color);
    }

    .coords-table th {
      color: var(--color-text-muted);
      font-weight: 600;
    }

    .btn-row {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
    }

    .btn-outline {
      background: transparent;
      border: 1px solid var(--border-color);
      color: var(--color-text-main);
    }

    .btn-outline:hover {
      border-color: var(--color-player);
      color: var(--color-player);
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
        <h1>Calibração do Tabuleiro via Web 📷</h1>
        <p class="header-subtitle">Marque os 4 cantos do tabuleiro diretamente na tela do seu navegador</p>
      </div>
    </div>
    
    <div style="display: flex; gap: 1rem; align-items: center;">
      <a href="index.php" class="btn btn-outline" style="padding: 0.5rem 1rem; font-size: 0.85rem; text-decoration: none;">
        ⬅️ Voltar ao Dashboard
      </a>
      <div class="status-badge">
        <div id="statusDot" class="status-dot online"></div>
        <span id="statusLabel">Online</span>
      </div>
    </div>
  </header>

  <main>
    <!-- Painel Esquerdo: Imagem Interativa da Câmera -->
    <div class="panel">
      <div class="panel-title">
        <span>Feed ao Vivo da Câmera</span>
        <span id="coordTooltip" style="font-size: 0.8rem; color: var(--color-player); font-weight: normal;">Clique na imagem para marcar os cantos</span>
      </div>

      <div class="interactive-camera-box" id="camBox" onclick="handleImageClick(event)">
        <img id="rawFeed" src="" alt="Carregando transmissão da câmera..." onload="updateOverlaySize()">
        <svg id="svgOverlay" class="svg-overlay"></svg>
      </div>

      <div style="font-size: 0.85rem; color: var(--color-text-muted); line-height: 1.5;">
        💡 <strong>Dica:</strong> Para calibrar com precisão, clique rigorosamente nos <strong>4 cantos do tabuleiro físico</strong> na ordem indicada no painel ao lado (SE ➔ SD ➔ ID ➔ IE).
      </div>
    </div>

    <!-- Painel Direito: Guia de Calibração e Controles -->
    <div class="panel">
      <div class="panel-title">Passo a Passo da Calibração</div>

      <div class="cal-instructions">
        <div class="step-item active" id="step1">
          <span class="step-number">1</span>
          <span><strong>Superior-Esquerdo (SE):</strong> Canto superior esquerdo do tabuleiro</span>
        </div>
        <div class="step-item" id="step2">
          <span class="step-number">2</span>
          <span><strong>Superior-Direito (SD):</strong> Canto superior direito do tabuleiro</span>
        </div>
        <div class="step-item" id="step3">
          <span class="step-number">3</span>
          <span><strong>Inferior-Direito (ID):</strong> Canto inferior direito do tabuleiro</span>
        </div>
        <div class="step-item" id="step4">
          <span class="step-number">4</span>
          <span><strong>Inferior-Esquerdo (IE):</strong> Canto inferior esquerdo do tabuleiro</span>
        </div>
      </div>

      <div class="panel-title" style="font-size: 1rem; border-top: 1px solid var(--border-color); padding-top: 1rem; margin-top: 0.5rem;">Coordenadas Selecionadas (Pixels)</div>

      <table class="coords-table">
        <thead>
          <tr>
            <th>Canto</th>
            <th>Rótulo</th>
            <th>Coordenada (X, Y)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>1º Clique</td>
            <td style="color: #10b981;">Superior-Esquerdo (SE)</td>
            <td id="p0_str" style="font-family: monospace;">-</td>
          </tr>
          <tr>
            <td>2º Clique</td>
            <td style="color: #f59e0b;">Superior-Direito (SD)</td>
            <td id="p1_str" style="font-family: monospace;">-</td>
          </tr>
          <tr>
            <td>3º Clique</td>
            <td style="color: #ef4444;">Inferior-Direito (ID)</td>
            <td id="p2_str" style="font-family: monospace;">-</td>
          </tr>
          <tr>
            <td>4º Clique</td>
            <td style="color: #8b5cf6;">Inferior-Esquerdo (IE)</td>
            <td id="p3_str" style="font-family: monospace;">-</td>
          </tr>
        </tbody>
      </table>

      <div class="btn-row">
        <button id="btnSave" class="btn btn-primary" style="flex: 1;" onclick="saveCalibration()" disabled>
          💾 Salvar Calibração
        </button>
        <button class="btn btn-outline" onclick="resetPoints()">
          🔄 Refazer Pontos
        </button>
        <button class="btn btn-outline" onclick="loadSavedCalibration()">
          📥 Carregar Atual
        </button>
      </div>

      <div class="panel-title" style="font-size: 1rem; border-top: 1px solid var(--border-color); padding-top: 1rem; margin-top: 0.5rem;">Console de Status</div>
      <div class="logs-container" id="logsBox">
        <div class="log-entry info">[SISTEMA] Aguardando marcação do 1º ponto (Superior-Esquerdo)...</div>
      </div>
    </div>
  </main>

  <footer>
    SENAI — Centro de Treinamento e Desenvolvimento da Indústria 4.0 • UR3 Universal Robots × OnRobot RG2
  </footer>

  <script>
    let clickedPoints = [];
    const pointColors = ['#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
    const pointLabels = ['SE (1)', 'SD (2)', 'ID (3)', 'IE (4)'];

    // Configura o feed bruto da câmera sem warping via Proxy PHP (porta 8000)
    const rawFeedImg = document.getElementById('rawFeed');
    rawFeedImg.src = 'api.php?action=stream_raw';

    function logEvent(msg, type = 'info') {
      const logsBox = document.getElementById('logsBox');
      const entry = document.createElement('div');
      entry.className = `log-entry ${type}`;
      const time = new Date().toLocaleTimeString();
      entry.innerText = `[${time}] ${msg}`;
      logsBox.appendChild(entry);
      logsBox.scrollTop = logsBox.scrollHeight;
    }

    // Clique na Imagem para capturar as coordenadas exatas da imagem original
    function handleImageClick(event) {
      if (clickedPoints.length >= 4) {
        logEvent('Os 4 pontos já foram marcados. Clique em "Refazer Pontos" se desejar reiniciar.', 'warning');
        return;
      }

      const rect = rawFeedImg.getBoundingClientRect();
      const clickX = event.clientX - rect.left;
      const clickY = event.clientY - rect.top;

      // Calcula as coordenadas reais da imagem (baseado nas dimensões nativas do vídeo)
      const scaleX = rawFeedImg.naturalWidth / rect.width;
      const scaleY = rawFeedImg.naturalHeight / rect.height;

      const realX = Math.round(clickX * scaleX);
      const realY = Math.round(clickY * scaleY);

      clickedPoints.push([realX, realY]);

      const idx = clickedPoints.length - 1;
      logEvent(`Ponto ${idx + 1}/4 (${pointLabels[idx]}) marcado: X=${realX}, Y=${realY}`, 'success');

      updateUI();
    }

    function updateUI() {
      // Atualiza tabela
      for (let i = 0; i < 4; i++) {
        const cell = document.getElementById(`p${i}_str`);
        if (clickedPoints[i]) {
          cell.innerText = `(${clickedPoints[i][0]}, ${clickedPoints[i][1]})`;
        } else {
          cell.innerText = '-';
        }
      }

      // Atualiza passos
      for (let i = 1; i <= 4; i++) {
        const item = document.getElementById(`step${i}`);
        item.className = 'step-item';
        if (i <= clickedPoints.length) {
          item.classList.add('done');
        } else if (i === clickedPoints.length + 1) {
          item.classList.add('active');
        }
      }

      // Habilita botão Salvar se houver 4 pontos
      document.getElementById('btnSave').disabled = clickedPoints.length !== 4;

      renderSVGOverlay();
    }

    // Desenha os marcadores e linhas no SVG Overlay sobre a imagem
    function renderSVGOverlay() {
      const svg = document.getElementById('svgOverlay');
      const rect = rawFeedImg.getBoundingClientRect();
      svg.setAttribute('viewBox', `0 0 ${rect.width} ${rect.height}`);

      let html = '';

      if (rawFeedImg.naturalWidth === 0) return;

      const scaleX = rect.width / rawFeedImg.naturalWidth;
      const scaleY = rect.height / rawFeedImg.naturalHeight;

      // Desenha o polígono conectando os pontos
      if (clickedPoints.length > 1) {
        let pointsStr = clickedPoints.map(p => `${p[0] * scaleX},${p[1] * scaleY}`).join(' ');
        if (clickedPoints.length === 4) {
          html += `<polygon points="${pointsStr}" fill="rgba(0, 212, 255, 0.15)" stroke="#00d4ff" stroke-width="2" stroke-dasharray="4 4" />`;
        } else {
          html += `<polyline points="${pointsStr}" fill="none" stroke="#00d4ff" stroke-width="2" />`;
        }
      }

      // Desenha os pinos/pontos
      clickedPoints.forEach((p, i) => {
        const cx = p[0] * scaleX;
        const cy = p[1] * scaleY;
        const color = pointColors[i];

        html += `
          <circle cx="${cx}" cy="${cy}" r="7" fill="${color}" stroke="#ffffff" stroke-width="2" />
          <text x="${cx + 10}" y="${cy - 8}" fill="${color}" font-weight="bold" font-size="14" filter="drop-shadow(0px 0px 3px #000)">${pointLabels[i]}</text>
        `;
      });

      svg.innerHTML = html;
    }

    function resetPoints() {
      clickedPoints = [];
      updateUI();
      logEvent('Seleção zerada. Aguardando marcação do 1º ponto...', 'info');
    }

    async function saveCalibration() {
      if (clickedPoints.length !== 4) return;

      logEvent('Enviando calibração para o servidor...', 'info');
      try {
        const res = await fetch('api.php?action=calibrate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ points: clickedPoints })
        });
        const data = await res.json();

        if (data.status === 'success') {
          logEvent('✓ CALIBRAÇÃO SALVA E APLICADA COM SUCESSO! 🎉', 'success');
          alert('Calibração salva com sucesso no sistema!');
        } else {
          logEvent(`Erro ao salvar: ${data.error || 'Erro no servidor'}`, 'error');
        }
      } catch (err) {
        logEvent('Erro de conexão ao salvar calibração.', 'error');
      }
    }

    async function loadSavedCalibration() {
      logEvent('Carregando calibração salva atualmente...', 'info');
      try {
        const res = await fetch('api.php?action=calibrate');
        const data = await res.json();
        if (data.corners && data.corners.length === 4) {
          clickedPoints = data.corners;
          updateUI();
          logEvent('✓ Calibração salva carregada no painel!', 'success');
        } else {
          logEvent('Nenhuma calibração previa encontrada.', 'warning');
        }
      } catch (err) {
        logEvent('Erro de comunicação ao carregar calibração.', 'error');
      }
    }

    function updateOverlaySize() {
      renderSVGOverlay();
    }

    window.addEventListener('resize', renderSVGOverlay);
    loadSavedCalibration();
  </script>
</body>
</html>
