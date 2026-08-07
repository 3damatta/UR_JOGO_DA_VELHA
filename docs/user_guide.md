# Manual de Utilização do Sistema

Este documento descreve como o operador do sistema (jogador ou instrutor) interage com a interface gráfica unificada em PHP/Python para gerenciar partidas e controlar o robô.

---

## 1. Inicializando o Sistema

Para ligar os servidores locais de controle do Jogo da Velha, execute no seu terminal:

```bash
cd "c:\Users\PC\OneDrive\Documentos\PROJETOS\Nova pasta\ur3_tictactoe"
bash scripts/start.sh
```

Isso ligará automaticamente:
* A API central e o thread da visão computacional (Python Flask, porta `5000`).
* A interface gráfica web (servidor embutido do PHP, porta `8000`).

Abra o seu navegador web favorito e acesse o endereço:
➔ **[http://localhost:8000](http://localhost:8000)** (ou o IP do Raspberry Pi na sua rede Wi-Fi, ex: `http://192.168.0.10:8000`).

---

## 2. Visão Geral do Dashboard

A interface web foi desenhada com um design escuro premium contendo dois blocos principais:

* **Painel Esquerdo (Visão da Câmera):** Exibe a transmissão em tempo real (MJPEG Stream) da câmera USB. Mostra a delimitação do tabuleiro e indica visualmente onde as peças estão sendo detectadas em tempo real.
* **Painel Direito (Jogo & Controles):**
  * **Tabuleiro Virtual (3x3):** Mostra a simulação digital do tabuleiro com cores neons destacadas (X em Azul, O em Laranja). 
  * **Estado da Partida:** Mostra banners informativos coloridos (Ex: "Aguardando Jogador", "Robô jogando", "Vitória do Robô").
  * **Botão "Iniciar / Reiniciar Jogo":** Reseta o tabuleiro lógico, limpa os contadores do detector de imagem e envia o robô de volta à posição de segurança (HOME).
  * **Console de Eventos:** Exibe logs rápidos com marcações de data e hora sobre cada evento do jogo (ex: peça detectada, jogada do robô, status offline/online).

---

## 3. Modos de Jogo

O sistema unificado suporta dois modos de operação para flexibilidade de demonstração:

### Modo 1: Jogo Físico por Visão Computacional (Automático)
Este é o modo padrão de operação do sistema utilizando a câmera:
1. Pressione o botão **"Iniciar / Reiniciar Jogo"** na tela. O robô irá para a posição HOME.
2. O jogador humano (X) faz sua jogada colocando fisicamente a **peça azul** no quadrado desejado do tabuleiro de madeira.
3. Não obstrua o tabuleiro com as mãos após colocar a peça. O sistema OpenCV confirmará a presença da peça após ela ficar estática por 8 frames e emitirá um aviso sonoro/visual na tela.
4. O robô calcula instantaneamente a resposta e executa a movimentação física automática para colocar a peça dele (laranja) no local calculado.
5. Repita o fluxo até que a partida termine em vitória de um dos lados ou em empate.

### Modo 2: Jogo Manual/Híbrido (Sem Câmera)
Se você deseja demonstrar o funcionamento físico do robô, mas não possui uma câmera conectada ou há problemas de iluminação na sala:
1. Pressione **"Iniciar / Reiniciar Jogo"** para zerar a partida.
2. Em vez de colocar uma peça no tabuleiro físico, clique no quadrado correspondente diretamente no **Tabuleiro Virtual 3x3** do navegador.
3. O clique registrará a sua jogada (X) no painel digital e disparará automaticamente o turno do robô.
4. O robô UR3 se moverá fisicamente e posicionará a peça real no tabuleiro físico na célula clicada!
5. Isso permite operar o sistema e fazer demonstrações públicas mesmo em ambientes com luz desfavorável para a visão computacional.

---

## 4. Desligando o Sistema

Para encerrar o sistema de jogo e liberar as portas de rede e a câmera USB, basta retornar ao terminal onde você executou o `start.sh` e pressionar:

```text
Ctrl + C
```

O script disparará o encerramento seguro e fechará as conexões do servidor Python e do servidor PHP automaticamente.
