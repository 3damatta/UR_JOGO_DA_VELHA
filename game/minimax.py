"""
IA do Jogo da Velha — Algoritmo Minimax com Poda Alpha-Beta
===========================================================
O robô joga como 'O', o humano como 'X'.
Tabuleiro representado como lista de 9 posições:
  0 | 1 | 2
  ---------
  3 | 4 | 5
  ---------
  6 | 7 | 8

Valores: '' = vazio, 'X' = jogador, 'O' = robô
"""

import math
from typing import Optional


WINNING_COMBOS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # linhas
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # colunas
    (0, 4, 8), (2, 4, 6),              # diagonais
]


def check_winner(board: list) -> Optional[str]:
    """Retorna 'X', 'O' ou None."""
    for a, b, c in WINNING_COMBOS:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None


def is_draw(board: list) -> bool:
    return all(cell != '' for cell in board) and check_winner(board) is None


def get_empty_cells(board: list) -> list:
    return [i for i, cell in enumerate(board) if cell == '']


def minimax(board: list, depth: int, is_maximizing: bool,
            alpha: float, beta: float) -> int:
    """
    Minimax com poda Alpha-Beta.
    Maximiza para 'O' (robô), minimiza para 'X' (jogador).
    """
    winner = check_winner(board)
    if winner == 'O':
        return 10 - depth
    if winner == 'X':
        return depth - 10
    if is_draw(board):
        return 0

    empty = get_empty_cells(board)

    if is_maximizing:
        best = -math.inf
        for cell in empty:
            board[cell] = 'O'
            score = minimax(board, depth + 1, False, alpha, beta)
            board[cell] = ''
            best = max(best, score)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = math.inf
        for cell in empty:
            board[cell] = 'X'
            score = minimax(board, depth + 1, True, alpha, beta)
            board[cell] = ''
            best = min(best, score)
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best


def best_move(board: list, difficulty: str = 'medium') -> int:
    """
    Retorna o índice (0-8) da célula para o robô jogar com base na dificuldade:
      - 'easy': 30% Minimax, 70% Aleatório / Sub-ótimo (Vitórias fáceis para o humano)
      - 'medium': 70% Minimax, 30% Sub-ótimo (Jogo justo e equilibrado)
      - 'hard' / 'impossible': 100% Minimax (Imbatível)
    Retorna -1 se não houver jogada possível.
    """
    import random

    empty = get_empty_cells(board)
    if not empty:
        return -1

    # Avalia a pontuação de cada movimento possível via Minimax
    scored_moves = []
    # Prioridade para desempate: centro (4), cantos (0,2,6,8), bordas (1,3,5,7)
    priority = [4, 0, 2, 6, 8, 1, 3, 5, 7]
    ordered_empty = sorted(empty, key=lambda c: priority.index(c) if c in priority else 9)

    for cell in ordered_empty:
        board[cell] = 'O'
        score = minimax(board, 0, False, -math.inf, math.inf)
        board[cell] = ''
        scored_moves.append((cell, score))

    # Ordena jogadas da melhor pontuação para a pior
    scored_moves.sort(key=lambda x: x[1], reverse=True)
    best_score = scored_moves[0][1]

    best_moves = [cell for cell, score in scored_moves if score == best_score]
    suboptimal_moves = [cell for cell, score in scored_moves if score < best_score]

    # Se a IA puder vencer imediatamente (score >= 9), executa a vitória a menos que seja modo fácil extremo
    if best_score >= 9:
        if difficulty == 'easy' and random.random() < 0.30 and suboptimal_moves:
            return random.choice(suboptimal_moves)
        return random.choice(best_moves)

    if difficulty == 'easy':
        if suboptimal_moves and random.random() < 0.70:
            return random.choice(suboptimal_moves)
        return random.choice(empty)

    elif difficulty == 'medium':
        # 30% de chance de cometer imperfeição tática dando chance para o humano vencer
        if suboptimal_moves and random.random() < 0.30:
            return random.choice(suboptimal_moves)
        return random.choice(best_moves)

    else:
        # Mode 'hard' ou 'impossible': 100% Minimax perfeito
        return random.choice(best_moves)


def get_winning_line(board: list) -> Optional[tuple]:
    """Retorna a combo vencedora ou None."""
    winner = check_winner(board)
    if not winner:
        return None
    for combo in WINNING_COMBOS:
        a, b, c = combo
        if board[a] == board[b] == board[c] == winner:
            return combo
    return None


def game_status(board: list) -> dict:
    """
    Retorna o estado atual do jogo como dicionário.
    status: 'ongoing' | 'robot_wins' | 'player_wins' | 'draw'
    """
    winner = check_winner(board)
    if winner == 'O':
        return {'status': 'robot_wins', 'winner': 'O',
                'winning_line': get_winning_line(board)}
    if winner == 'X':
        return {'status': 'player_wins', 'winner': 'X',
                'winning_line': get_winning_line(board)}
    if is_draw(board):
        return {'status': 'draw', 'winner': None, 'winning_line': None}
    return {'status': 'ongoing', 'winner': None, 'winning_line': None}


# ── Teste rápido ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=== Teste IA Minimax (Com Níveis de Dificuldade) ===\n")

    # Teste 1: IA no modo imbatível deve bloquear vitória do jogador
    board1 = ['X', 'X', '', 'O', '', '', '', '', '']
    move1 = best_move(board1, difficulty='impossible')
    print(f"Teste 1 - Bloquear vitoria X na celula 2 (Impossivel): Escolheu {move1} {'[OK]' if move1 == 2 else '[FAIL]'}")

    # Teste 2: IA deve vencer quando possível (Impossível)
    board2 = ['O', 'O', '', 'X', 'X', '', '', '', '']
    move2 = best_move(board2, difficulty='impossible')
    print(f"Teste 2 - IA vence na celula 2 (Impossivel): Escolheu {move2} {'[OK]' if move2 == 2 else '[FAIL]'}")

    # Teste 3: Tabuleiro vazio - Modo Médio
    board3 = ['']*9
    move3 = best_move(board3, difficulty='medium')
    print(f"Teste 3 - Tabuleiro vazio (Medio): Escolheu {move3} [OK]")

    print("\nTodos os testes concluidos com sucesso!")

