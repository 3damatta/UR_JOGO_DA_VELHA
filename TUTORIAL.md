# Manual de Utilização e Operação do Usuário — UR3 Jogo da Velha 🤖×🎮

Este é o **Manual do Usuário Final** para operação, calibração da câmera e configuração de posições do robô colaborativo **Universal Robots UR3**.

> [!NOTE]
> **100% ACESSÍVEL VIA NAVEGADOR WEB (0 Instalações / Sem Teclado / Sem Monitor / Sem SSH)**  
> O Raspberry Pi já está pré-configurado com inicialização automática (`systemd`). Ao ligá-lo na tomada, todo o sistema (Rede Hotspot, Visão Computacional, Backend Python e Dashboard Web PHP) inicia sozinho em 30 segundos.

---

## 📋 Sumário
1. [Conexão e Endereços de Acesso pelo Computador/Celular](#1-conexão-e-endereços-de-acesso-pelo-computadorcelular)
2. [Calibração da Câmera pelo Navegador](#2-calibração-da-câmera-pelo-navegador)
3. [Configuração dos Pontos de Rota do Robô (Regras Fundamentais)](#3-configuração-dos-pontos-de-rota-do-robô-regras-fundamentais)
   - [A) Posição HOME (Inicial)](#a-posição-home-posição-inicial-de-segurança)
   - [B) Ponto de CAPTURA (PICK / Estoque) — GARRA ABERTA](#b-ponto-de-captura-pick--estoque-de-peças--⚠️-garra-aberta)
   - [C) Células 0 a 8 do Tabuleiro — GARRA FECHADA COM A PEÇA](#c-células-0-a-8-do-tabuleiro--⚠️-garra-fechada-segurando-a-peça)
4. [Validação de Movimentos e Testes de Garra](#4-validação-de-movimentos-e-testes-de-garra)
5. [Como Jogar (Fluxo da Partida)](#5-como-jogar-fluxo-da-partida)

---

## 1. Conexão e Endereços de Acesso pelo Computador/Celular

1. Ligue o Raspberry Pi na tomada.
2. No seu computador, notebook, tablet ou smartphone, conecte-se à rede Wi-Fi **Hotspot do Raspberry Pi** (ou à rede local do laboratório).
3. Abra o navegador de sua preferência (Google Chrome, Microsoft Edge ou Safari) e digite o endereço IP do Raspberry Pi na porta **8000**:

```text
http://192.168.4.1:8000
```
*(Nota: Se o IP do seu Hotspot for diferente, substitua `192.168.4.1` pelo IP atribuído ao Pi, ex: `http://10.42.0.1:8000`)*

---

### 🌐 Telas Principais da Dashboard:

* 🎮 **Painel Principal do Jogo:** `http://192.168.4.1:8000/index.php`  
  *(Acompanhamento do jogo, tabuleiro virtual, feed da câmera e seletor de dificuldade).*
* 📷 **Calibração da Câmera:** `http://192.168.4.1:8000/calibrate.php`  
  *(Ajuste de perspectiva do tabuleiro 3x3 clicando direto na tela).*
* 📍 **Configuração de Posições & Testes:** `http://192.168.4.1:8000/positions.php`  
  *(Configuração de ângulos de articulação do UR3, captura automática do robô e testes de movimento).*

---

## 2. Calibração da Câmera pelo Navegador

A calibração alinha o campo de visão da câmera USB com o tabuleiro físico de 3x3 posições.

1. No navegador, acesse a tela de calibração:  
   `http://192.168.4.1:8000/calibrate.php` *(ou clique no botão **📷 Calibrar Câmera** no cabeçalho)*.
2. Na imagem da câmera exibida na tela, dê 4 cliques com o mouse marcando exatamente os 4 cantos externos do tabuleiro físico na seguinte sequência:
   - **1º Clique:** Canto Superior-Esquerdo (SE) 🟢
   - **2º Clique:** Canto Superior-Direito (SD) 🟡
   - **3º Clique:** Canto Inferior-Direito (ID) 🔴
   - **4º Clique:** Canto Inferior-Esquerdo (IE) 🟣
3. Clique no botão **`💾 Salvar Calibração`**. A calibração é salva e aplicada instantaneamente no sistema.

---

## 3. Configuração dos Pontos de Rota do Robô (Regras Fundamentais)

Acesse a página de gerenciamento de posições:  
`http://192.168.4.1:8000/positions.php` *(ou clique no botão **📍 Posições & Testes** no cabeçalho)*.

> [!TIP]
> **COMO CAPTURAR A POSIÇÃO DO ROBÔ AUTOMATICAMENTE:**  
> Leve o robô fisicamente até a posição desejada (usando o botão *Freedrive* atrás do Teach Pendant ou os direcionais de articulação em Modo Manual). Com o robô parado no ponto certo, vá na Dashboard e clique no botão azul **`🤖 Capturar Posição Atual`** (ou **`🤖 Capturar`**) no cartão correspondente. Os 6 ângulos reais do robô serão preenchidos automaticamente!

---

### A) Posição HOME (Posição Inicial de Segurança)

* **Descrição:** É o ponto neutro e elevado onde o robô aguarda as jogadas com segurança.
* **Como Posicionar o Robô:** Mova o robô para uma altura segura no ar, centralizado sobre o tabuleiro, garantindo que o braço e a garra tenham espaço livre para girar sem colidir com peças, câmeras ou o tabuleiro.
* **Como Salvar:**
  1. Clique em **`🤖 Capturar Posição Atual`** no cartão **HOME POSE**.
  2. Clique em **`💾 Salvar Home`**.

---

### B) Ponto de CAPTURA (PICK / Estoque de Peças) — ⚠️ GARRA ABERTA

> [!CAUTION]
> **REGRA OBRIGATÓRIA PARA O PONTO DE CAPTURA (PICK):**  
> Este ponto **DEVE SER SALVO COM A GARRA TOTALMENTE ABERTA** sobre a peça no estoque de retirada!

* **Passo a Passo de Salvamento:**
  1. No painel de topo da tela `positions.php`, clique em **`✋ Abrir Garra`** (ou abra a garra OnRobot pelo Teach Pendant).
  2. Mova o robô até encaixar a garra **aberta** exatamente envolta da peça de estoque de onde o robô irá retirar a peça.
  3. No cartão **PONTO DE CAPTURA (PICK)**, clique em **`🤖 Capturar Posição Atual`**.
  4. Clique em **`💾 Salvar Pick`**.

* **Por que com a garra aberta?**  
  Durante a partida, o robô descerá até essa altura exata com a garra aberta, fechará a garra OnRobot para prender a peça e subirá. Se você salvar esse ponto com a garra fechada, a garra colidirá na peça ao tentar descer!

---

### C) Células 0 a 8 do Tabuleiro — ⚠️ GARRA FECHADA SEGURANDO A PEÇA

> [!IMPORTANT]
> **REGRA OBRIGATÓRIA PARA AS 9 CÉLULAS DO TABULEIRO (0 A 8):**  
> Os pontos das células do tabuleiro **DEVEM SER SALVOS COM O ROBÔ SEGURANDO A PEÇA PELA GARRA FECHADA**, encostando a base da peça suavemente sobre a célula física do tabuleiro!

* **Passo a Passo de Salvamento:**
  1. Prenda a peça na garra OnRobot clicando em **`✊ Fechar Garra`** no topo da tela (ou feche a garra pelo Teach Pendant segurando uma peça).
  2. Mova o robô até a célula desejada (exemplo: **Célula 0 - Superior Esquerdo**), encostando a base da peça levemente na superfície do tabuleiro.
  3. No cartão da célula correspondente (ex: **Célula 0**), clique em **`🤖 Capturar`**.
  4. Clique em **`💾 Salvar`**.
  5. Repita o procedimento para as demais células (**Células 1 a 8**).
  6. Ao finalizar todas as posições, clique no botão superior **`💾 Salvar TODAS as Posições`**.

* **Por que com a peça segurada na garra?**  
  Como a garra segura a peça pela lateral, salvar o ponto com a peça já presa na garra garante a calibração perfeita da altura Z (toque no tabuleiro) e do alinhamento central da peça dentro do quadrado da célula.

---

## 4. Validação de Movimentos e Testes de Garra

Antes de iniciar a primeira partida com o robô, utilize os botões de teste da página `positions.php` para validar as posições salvas:

* **`🏠 Mover para HOME`**: Retorna o braço do robô para a pose inicial com 1 clique.
* **`🎯 Mover Robô Aqui` / `🎯 Mover`**: Envia o braço do UR3 até os 6 ângulos salvos naquela posição para você conferir visualmente o alinhamento.
* **`🤖 Pick & Place`**: Executa o teste real completo para aquela célula (Mover até o Pick ➔ Fechar Garra ➔ Mover até a Célula ➔ Abrir Garra ➔ Retornar HOME).
* **`✋ Abrir Garra` / `✊ Fechar Garra`**: Testa a abertura e fechamento pneumático/elétrico da garra OnRobot RG2/RG6.
* **`📜 Script`**: Exibe o código URScript gerado para simulação Dry-Run (sem mover o robô).

> [!WARNING]
> **DICA DE SEGURANÇA:** Nos primeiros testes de movimento físico, mantenha a velocidade do UR3 no Teach Pendant em **20%** e fique com a mão próxima ao botão de parada de emergência (*E-Stop*).

---

## 5. Como Jogar (Fluxo da Partida)

1. Acesse o Painel Principal do Jogo:  
   `http://192.168.4.1:8000/index.php`
2. Selecione a dificuldade desejada do robô no menu suspenso:
   - **Fácil 🟢:** Robô comete pequenos erros estratégicos (Vitória Humana Provável).
   - **Médio 🟡:** Jogo justo e equilibrado.
   - **MODO HERÓI ⚡:** IA Minimax Impossível (Empate ou Vitória do Robô).
3. Clique em **`Iniciar / Reiniciar Jogo`**. O robô irá para a pose **HOME**.
4. O jogador humano faz a sua jogada colocando a peça azul (**X**) no tabuleiro físico (ou clicando no tabuleiro virtual no navegador).
5. O robô reconhece a jogada via câmera, escolhe a melhor casa com IA, busca a peça laranja (**O**) no estoque e faz a jogada física no tabuleiro.
6. Acompanhe o resultado da partida e o status em tempo real no console de eventos da tela!
