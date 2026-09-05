import chess

from .schemas import MoveIntent


class GameError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)

    def payload(self) -> dict:
        return {"type": "error", "code": self.code, "message": self.message}


def color_name(color: chess.Color) -> str:
    return "white" if color else "black"


def outcome(board: chess.Board) -> chess.Outcome | None:
    result = board.outcome()
    if result:
        return result
    # V1 finaliza automaticamente quando a condição já existe no tabuleiro.
    # Não antecipa empates por uma jogada que ainda não foi feita.
    if board.is_fifty_moves():
        return chess.Outcome(chess.Termination.FIFTY_MOVES, None)
    if board.is_repetition(3):
        return chess.Outcome(chess.Termination.THREEFOLD_REPETITION, None)
    return None


def play(board: chess.Board, color: chess.Color, intent: MoveIntent) -> str:
    if outcome(board):
        raise GameError("GAME_OVER", "A partida já terminou.")
    if board.turn != color:
        raise GameError("NOT_YOUR_TURN", "Agora é a vez do outro jogador.")
    source = chess.parse_square(intent.from_square)
    piece = board.piece_at(source)
    if piece is None:
        raise GameError("EMPTY_SQUARE", "Escolha uma casa com uma peça sua.")
    if piece.color != color:
        raise GameError("OPPONENT_PIECE", "Essa peça pertence ao outro jogador.")
    move = chess.Move.from_uci(intent.from_square + intent.to + (intent.promotion or ""))
    if piece.piece_type == chess.PAWN and chess.square_rank(move.to_square) in (0, 7) and not intent.promotion:
        raise GameError("PROMOTION_REQUIRED", "Escolha dama, torre, bispo ou cavalo para promover.")
    if move not in board.legal_moves:
        if board.is_pseudo_legal(move) and board.is_into_check(move):
            raise GameError("KING_IN_CHECK", "Seu rei continuaria em xeque ou ficaria sob ataque.")
        raise GameError("ILLEGAL_MOVE", "Essa jogada não é permitida. Observe os destinos destacados.")
    san = board.san(move)
    board.push(move)
    return san


def board_state(board: chess.Board) -> dict:
    result = outcome(board)
    return {
        "fen": board.fen(),
        "turn": color_name(board.turn),
        "last_move": board.peek().uci() if board.move_stack else None,
        "ply": len(board.move_stack),
        "check": board.is_check(),
        "check_square": chess.square_name(board.king(board.turn)) if board.is_check() else None,
        "status": "finished" if result else "playing",
        "result": result.result() if result else None,
        "termination": result.termination.name.lower() if result else None,
        "winner": color_name(result.winner) if result and result.winner is not None else None,
        "legal_moves": [move.uci() for move in board.legal_moves] if not result else [],
    }
