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


def best_move(board: list) -> int:
    """
    Retorna o índice (0-8) da melhor célula para o robô jogar.
    Retorna -1 se não houver jogada possível.
    """
    empty = get_empty_cells(board)
    if not empty:
        return -1

    best_score = -math.inf
    chosen_cell = empty[0]

    # Preferência por centro, depois cantos, depois bordas
    priority = [4, 0, 2, 6, 8, 1, 3, 5, 7]
    ordered = sorted(empty, key=lambda c: priority.index(c) if c in priority else 9)

    for cell in ordered:
        board[cell] = 'O'
        score = minimax(board, 0, False, -math.inf, math.inf)
        board[cell] = ''
        if score > best_score:
            best_score = score
            chosen_cell = cell

    return chosen_cell


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
    import json

    print("=== Teste IA Minimax ===\n")

    # Teste 1: IA deve bloquear vitória do jogador
    board1 = ['X', 'X', '', 'O', '', '', '', '', '']
    move1 = best_move(board1)
    print(f"Teste 1 - Bloquear vitória X na célula 2: Escolheu {move1} {'✓' if move1 == 2 else '✗'}")

    # Teste 2: IA deve vencer quando possível
    board2 = ['O', 'O', '', 'X', 'X', '', '', '', '']
    move2 = best_move(board2)
    print(f"Teste 2 - IA vence na célula 2: Escolheu {move2} {'✓' if move2 == 2 else '✗'}")

    # Teste 3: Tabuleiro vazio - IA escolhe centro (4)
    board3 = ['']*9
    move3 = best_move(board3)
    print(f"Teste 3 - Tabuleiro vazio, deve escolher centro (4): Escolheu {move3} {'✓' if move3 == 4 else '✗'}")

    print("\nTodos os testes concluídos!")
