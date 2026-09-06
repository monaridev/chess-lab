"""Curated lessons. Replay intentions against server-owned positions, never client FENs."""
from dataclasses import dataclass
from typing import Annotated, Literal

import chess
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from .game import GameError, board_state, play
from .hints import build_plan
from .schemas import MoveIntent


@dataclass(frozen=True)
class Exercise:
    title: str
    objective: str
    fen: str
    answers: tuple[str, ...]
    concept: str
    success: str
    reply: str | None = None


@dataclass(frozen=True)
class Chapter:
    id: str
    title: str
    exercises: tuple[Exercise, ...]


def position(*moves: str) -> str:
    board = chess.Board()
    for move in moves:
        board.push_uci(move)
    return board.fen()


def exercise(title, objective, fen, answers, concept, success, reply=None):
    return Exercise(title, objective, fen, tuple(answers.split()), concept, success, reply)


CHAPTERS = (
    Chapter("movimentos", "Movimentos das peças", (
        exercise("Peão: o primeiro passo", "Avance o peão da coluna e para ocupar o centro.", chess.STARTING_FEN, "e2e4",
                 "O peão avança uma casa; na casa inicial, pode avançar duas se o caminho estiver livre. Captura uma casa na diagonal, nunca para trás.", "Você ocupou o centro e abriu uma diagonal para o bispo."),
        exercise("Torre: linhas retas", "Capture o peão indefeso com a torre.", "7k/8/8/8/p7/8/8/R3K3 w - - 0 1", "a1a4",
                 "A torre percorre colunas e fileiras, sem saltar peças.", "A torre percorreu a coluna e capturou um peão sem defesa."),
        exercise("Bispo: diagonais", "Capture o peão indefeso com o bispo.", "7k/8/8/8/5p2/8/8/2B1K3 w - - 0 1", "c1f4",
                 "O bispo anda nas diagonais e permanece na mesma cor de casa. Não salta peças.", "Você seguiu a diagonal até o alvo."),
        exercise("Cavalo: um salto em L", "Desenvolva o cavalo do rei para uma casa que ataque o centro.", chess.STARTING_FEN, "g1f3",
                 "O cavalo anda duas casas numa direção e uma para o lado. É a única peça que salta outras peças.", "O cavalo saltou os peões e passou a controlar o centro."),
        exercise("Dama: duas formas de andar", "Capture a torre sem defesa usando a dama.", "7k/8/8/7r/8/8/8/3QK3 w - - 0 1", "d1h5",
                 "A dama combina linhas retas e diagonais, sem saltar peças.", "A dama ficou ativa."),
        exercise("Rei: uma casa segura", "Capture o peão desprotegido com seu rei.", "7k/8/8/8/8/8/4p3/4K3 w - - 0 1", "e1e2",
                 "O rei anda uma casa em qualquer direção, mas nunca pode entrar em uma casa atacada.", "Seu rei capturou sem entrar em ataque."),
    )),
    Chapter("xeque", "Xeque e xeque-mate", (
        exercise("Primeiro, proteja o rei", "Seu rei está em xeque. Capture o atacante com a torre.", "k7/8/8/8/8/8/4r2R/4K3 w - - 0 1", "h2e2",
                 "Xeque é um ataque ao rei. Você precisa fugir, capturar o atacante ou bloquear a linha.", "O ataque ao rei foi resolvido."),
        exercise("Feche a rede de mate", "Encontre um xeque de dama que não permita nenhuma resposta.", "7k/5K2/6Q1/8/8/8/8/8 w - - 0 1", "g6g7 g6g8 g6h6 g6h5",
                 "Mate exige xeque e nenhuma resposta legal. Sem xeque e sem lances legais, é afogamento: empate.", "Xeque-mate! O rei está atacado e não pode fugir, bloquear ou capturar."),
    )),
    Chapter("material", "Valor das peças e peças indefesas", (
        exercise("Conte antes de capturar", "Capture a dama indefesa com sua torre.", "7k/8/8/8/q7/8/8/R3K3 w - - 0 1", "a1a4",
                 "Valores aproximados: peão 1, cavalo 3, bispo 3, torre 5, dama 9. O rei não tem preço. Conte também as recapturas.", "Você ganhou uma dama (9) com a torre (5), sem recaptura direta."),
        exercise("Sua peça também precisa de cuidado", "Sua torre está atacada pelo bispo. Leve-a para a coluna b, fora da diagonal de ataque.", "7k/8/8/8/8/8/1b6/R3K3 w - - 0 1", "a1b1",
                 "Uma peça atacada e sem defesa pode ser perdida. Mover, defender ou capturar o atacante são planos a comparar.", "Você tirou a torre da diagonal de ataque e manteve sua atividade."),
    )),
    Chapter("abertura", "Abertura saudável: centro, desenvolvimento e roque", (
        exercise("Dispute o centro", "Ocupe o centro com um peão central.", chess.STARTING_FEN, "e2e4 d2d4",
                 "Peões centrais ganham espaço e abrem caminho para bispos. Depois desenvolva as peças e cuide do rei.", "Um peão central abriu linhas para suas peças."),
        exercise("Traga uma peça para o jogo", "Desenvolva o cavalo do rei atacando o peão central adversário.", position("e2e4", "e7e5"), "g1f3",
                 "Desenvolver é tirar as peças da primeira fileira para casas úteis. Evite mover sempre a mesma peça.", "Seu cavalo ataca o centro e você está mais perto de rocar."),
        exercise("Rei protegido, torre ativa", "Faça o roque pequeno para proteger seu rei.", position("e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6"), "e1g1",
                 "No roque, mova o rei duas casas em direção à torre. Rei e torre não podem ter se movido; o caminho deve estar livre e o rei não pode estar, passar ou terminar em xeque.", "Rei em g1, torre em f1: os dois cooperaram em um único lance."),
    )),
    Chapter("ameacas", "Garfos e ameaças simples", (
        exercise("Dois alvos, um cavalo", "Crie um garfo de cavalo contra o rei e a torre.", "3k3r/8/8/4N3/8/8/8/4K3 w - - 0 1", "e5f7",
                 "Um garfo ataca dois alvos de uma vez. Um xeque obriga o adversário a cuidar do rei primeiro.", "Seu cavalo criou duas ameaças ao mesmo tempo."),
        exercise("Uma ameaça com segurança", "Desenvolva seu cavalo para atacar a dama, sem oferecer o cavalo.", "7k/8/8/3q4/8/8/8/1N2K3 w - - 0 1", "b1c3",
                 "Antes de criar uma ameaça, confira a resposta adversária. Uma peça atacada pode fugir, defender ou capturar.", "Você criou uma ameaça. O adversário ainda pode responder: ameaça não é ganho garantido."),
    )),
)

# A complete short demonstration, not an engine opponent or an opening recommendation.
_guided = (
    ("Centro primeiro", "Ocupe o centro com o peão do rei.", "e2e4", "e7e5", "Peões centrais abrem linhas e dão espaço às peças."),
    ("Desenvolva o bispo", "Desenvolva o bispo para mirar o peão mais sensível perto do rei preto.", "f1c4", "b8c6", "O peão f7 começa defendido apenas pelo rei. O bispo pode mirar essa diagonal."),
    ("Reconheça uma ameaça de mate", "Neste roteiro, coloque a dama na coluna h para criar uma ameaça junto do bispo.", "d1h5", "g8f6", "Sair cedo com a dama costuma perder tempos. Aqui estudamos uma armadilha: as pretas poderiam defender com g6, mas o roteiro mostra uma resposta que ignora a ameaça."),
    ("Veja além do ataque à dama", "O cavalo ameaça sua dama. Existe um xeque-mate imediato que responde a isso?", "h5f7", None, "Confira xeques antes de recuar: o bispo apoia a dama, e o rei adversário não consegue capturá-la."),
)
_board = chess.Board()
_steps = []
for title, objective, move, reply, concept in _guided:
    _steps.append(exercise(title, objective, _board.fen(), move, concept,
                           "Você verificou a ameaça e encontrou o plano." if reply else "Xeque-mate! Você reconheceu o perigo em f7. Na sua partida, prefira desenvolver e rocar; esta armadilha depende de erros na defesa.", reply))
    _board.push_uci(move)
    if reply:
        _board.push_uci(reply)
CHAPTERS += (Chapter("guiada", "Partida guiada", tuple(_steps)),)
CATALOG = {chapter.id: chapter for chapter in CHAPTERS}

Uci = Annotated[str, StringConstraints(pattern=r"^[a-h][1-8][a-h][1-8][qrbn]?$")]


class LearningIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    moves: list[Uci] = Field(default_factory=list, max_length=32)
    action: Literal["state", "move", "hint", "reveal"] = "state"
    move: Uci | None = None
    level: int = Field(default=0, ge=0, le=4)


def apply(ex: Exercise, uci: str) -> chess.Board:
    board = chess.Board(ex.fen)
    play(board, chess.WHITE, MoveIntent.model_validate({"type": "move", "from": uci[:2], "to": uci[2:4], "promotion": uci[4:] or None}))
    if uci not in ex.answers:
        raise GameError("TRY_AGAIN", "Esse lance é legal, mas ainda não resolve o objetivo. Pense com calma e compare outra possibilidade.")
    if ex.reply:
        board.push_uci(ex.reply)
    return board


def evaluate(chapter: Chapter, body: LearningIntent) -> dict:
    if len(body.moves) > len(chapter.exercises):
        raise GameError("INVALID_PROGRESS", "Progresso incompatível. Reinicie este capítulo.")
    after = None
    for ex, move in zip(chapter.exercises, body.moves):
        after = apply(ex, move)
    moves = list(body.moves)
    feedback = None
    if body.action == "move":
        if len(moves) == len(chapter.exercises) or body.move is None:
            raise GameError("INVALID_STEP", "Escolha uma lição em andamento.")
        ex = chapter.exercises[len(moves)]
        after = apply(ex, body.move)
        feedback = ex.success
        moves.append(body.move)
    complete = len(moves) == len(chapter.exercises)
    ex = chapter.exercises[min(len(moves), len(chapter.exercises) - 1)]
    board = after if complete else chess.Board(ex.fen)
    result = {"chapter": chapter.id, "moves": moves, "step": len(moves), "total": len(chapter.exercises),
              "complete": complete, "title": ex.title, "objective": ex.objective,
              "board": board_state(board), "feedback": feedback, "level": 0,
              "after": board_state(after) if body.action == "move" else None}
    if body.action in ("hint", "reveal") and not complete:
        plan = build_plan(board, chess.Move.from_uci(ex.answers[0]))
        if body.action == "hint":
            level = min(body.level + 1, 4)
            result.update(level=level, hints=[plan.messages[0], plan.messages[1], ex.concept, plan.messages[3]][:level])
        elif body.level == 4:
            result.update(level=4, reveal={"move": plan.move, "message": f"Uma possibilidade: {plan.san} ({plan.move[:2]} → {plan.move[2:4]}). {ex.concept}"})
        else:
            raise GameError("HINTS_FIRST", "Explore as quatro pistas antes de revelar uma possibilidade.")
    return result


router = APIRouter(prefix="/api/learn")


@router.get("")
def catalog():
    return [{"id": c.id, "title": c.title, "total": len(c.exercises)} for c in CHAPTERS]


@router.post("/{chapter_id}")
def lesson(chapter_id: str, body: LearningIntent):
    chapter = CATALOG.get(chapter_id)
    if chapter is None:
        raise GameError("UNKNOWN_LESSON", "Capítulo não encontrado.")
    try:
        return evaluate(chapter, body)
    except GameError as exc:
        # A legal experiment missing the objective is normal teaching feedback.
        if exc.code == "TRY_AGAIN" and body.action == "move":
            return {"accepted": False, "message": exc.message}
        raise
