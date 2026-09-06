"""Evidence-based post-move teaching. Scores measure; legal positions explain."""
from collections import Counter
from dataclasses import asdict, dataclass
import math

import chess

from .hints import NAMES, VALUES, build_plan, describe

LABELS = {"brilliant": "Genial", "excellent": "Excelente", "very_good": "Muito boa",
          "good": "Boa", "interesting": "Interessante", "inaccuracy": "Imprecisa",
          "mistake": "Erro", "blunder": "Grave"}
POSES = {"brilliant": "elogiando", "excellent": "elogiando", "very_good": "elogiando",
         "good": "feliz", "interesting": "pensando", "inaccuracy": "pensando",
         "mistake": "alerta", "blunder": "alerta"}


@dataclass(frozen=True)
class Evidence:
    concept: str
    text: str
    priority: int
    negative: bool = False


def hanging(board, color):
    """Legal captures with no legal immediate recapture, not pseudo-attacks."""
    probe = board.copy(stack=False)
    probe.turn = not color
    found = set()
    for capture in list(probe.legal_moves):
        victim = probe.piece_at(capture.to_square)
        if not victim or victim.color != color or not probe.is_capture(capture):
            continue
        after = probe.copy(stack=False)
        after.push(capture)
        if not any(m.to_square == capture.to_square and after.is_capture(m) for m in after.legal_moves):
            found.add(capture.to_square)
    return found


def evidence(before, move, after, best, played, loss):
    color = before.turn
    piece = before.piece_at(move.from_square)
    name = NAMES[piece.piece_type]
    article = "a" if piece.piece_type in (chess.ROOK, chess.QUEEN) else "o"
    own = "Sua" if article == "a" else "Seu"
    dest = chess.square_name(move.to_square)
    facts = []
    def add(concept, text, priority, negative=False):
        facts.append(Evidence(concept, text, priority, negative))
    if after.is_checkmate():
        add("mate encontrado", "Você deu xeque e fechou todas as respostas do rei: xeque-mate!", 0)
    elif best.mate is not None and best.mate > 0 and (played.mate is None or played.mate < 0):
        add("mate perdido", "Havia uma sequência de mate, mas esse lance deixou essa oportunidade escapar.", 0, True)
    if played.mate is not None and played.mate < 0 and not (best.mate is not None and best.mate < 0):
        add("segurança do rei", "Esse lance permitiu uma sequência de xeques que leva ao mate contra seu rei.", 0, True)
    if played.mate is not None and played.mate > 0 and best.mate is None:
        add("ameaça de mate", "Seu lance criou uma sequência de ataque que pode terminar em xeque-mate.", 0)
    # Material in the actual best reply, grounded in the after-position.
    if loss > 60 and played.pv:
        reply = played.pv[0]
        victim = after.piece_at(reply.to_square)
        if reply in after.legal_moves and victim and victim.color == color and after.is_capture(reply):
            add("material em risco", f"Depois desse lance, o adversário pode capturar {describe(after, reply.to_square)}.", 2, True)
    exposed = hanging(after, color)
    old = hanging(before, color)
    for sq in sorted(exposed, key=lambda s: -VALUES[after.piece_type_at(s)]):
        if loss > 60:
            ignored = sq in old and sq != move.to_square
            add("ameaça ignorada" if ignored else "peça sem defesa",
                f"Esse lance {'manteve' if ignored else 'deixou'} {describe(after, sq)} sob ataque e sem recaptura disponível.", 3, True)
    if before.is_capture(move):
        victim = chess.PAWN if before.is_en_passant(move) else before.piece_type_at(move.to_square)
        add("captura desfavorável" if loss > 120 else "captura",
            f"Você capturou {NAMES[victim]} com {name} em {dest}" + (", mas a continuação favorece o adversário." if loss > 120 else "."), 4, loss > 120)
    if move.promotion:
        add("promoção", f"Seu peão chegou a {dest} e virou {NAMES[move.promotion]}.", 2)
    plan = build_plan(before, move, "stockfish")
    topic = plan.concept
    if topic == "garfo":
        targets = [s for s in after.attacks(move.to_square) if after.color_at(s) == (not color) and after.piece_type_at(s) != chess.PAWN]
        add("garfo", f"{own} {name} em {dest} ataca {describe(after, targets[0])} e {describe(after, targets[1])} ao mesmo tempo.", 3)
    if topic == "cravada":
        pinned = [s for s in after.attacks(move.to_square) if after.color_at(s) == (not color) and after.is_pinned(not color, s) and not before.is_pinned(not color, s)]
        if pinned:
            add("cravada", f"Você cravou {describe(after, pinned[0])} à defesa do rei.", 3)
    if before.is_castling(move):
        add("roque", f"Você fez o roque: rei em {dest} e torre mais perto do centro.", 5)
    if before.is_check():
        add("defesa do rei", f"Seu lance de {name} para {dest} resolveu o xeque.", 5)
    if before.is_attacked_by(not color, move.from_square) and not after.is_attacked_by(not color, move.to_square):
        add("peça salva", f"Você tirou {article} {name} do ataque e chegou a {dest} sem ataque direto.", 4)
    central = chess.SquareSet([chess.D4, chess.E4, chess.D5, chess.E5])
    gained = (after.attacks(move.to_square) & central) - (before.attacks(move.from_square) & central)
    development = piece.piece_type in (chess.KNIGHT, chess.BISHOP) and chess.square_rank(move.from_square) == (0 if color else 7) and chess.square_rank(move.to_square) != (0 if color else 7)
    if development:
        add("desenvolvimento", f"Você desenvolveu {article} {name} para {dest}" + (" e aumentou seu controle do centro." if gained else "."), 6)
    if gained or (piece.piece_type == chess.PAWN and move.to_square in central):
        add("centro", f"{own} {name} em {dest} {'ocupa o' if move.to_square in central else 'passou a atacar mais casas do'} centro.", 6)
    if piece.piece_type == chess.ROOK:
        pawns = after.pieces(chess.PAWN, color) & chess.SquareSet(chess.BB_FILES[chess.square_file(move.to_square)])
        if not pawns:
            add("coluna aberta ou semiaberta", f"Sua torre em {dest} está numa coluna sem peões seus bloqueando o caminho.", 7)
    if after.is_check() and not after.is_checkmate():
        add("xeque", f"{own} {name} em {dest} deu xeque; o adversário precisa proteger o rei.", 5)
    # Always position-specific; never random praise or an unsupported diagnosis.
    reach = len(after.attacks(move.to_square))
    add("atividade", f"{own} {name} em {dest} influencia {reach} casas" + (", mas a análise encontrou uma continuação mais favorável antes desse lance." if loss > 60 else "."), 9, loss > 60)
    return sorted(facts, key=lambda f: (f.priority, not f.negative))


def adjusted_loss(before_cp, after_cp):
    raw = max(0, before_cp - after_cp)
    # Compress concessions only when both positions remain decisively won/lost.
    if before_cp * after_cp > 0 and min(abs(before_cp), abs(after_cp)) > 600:
        raw *= max(.15, 600 / min(abs(before_cp), abs(after_cp)))
    return min(1200, raw)


def classify(loss, *, forced=False, mate_found=False, mate_lost=False, allows_mate=False,
             tactical=False, unique=False, sacrifice=False):
    if mate_found or forced:
        return "excellent"
    if mate_lost or allows_mate:
        return "blunder"
    if loss <= 12:
        return "brilliant" if unique and sacrifice and tactical else "excellent"
    if loss <= 30:
        return "very_good"
    if loss <= 60:
        return "good"
    if loss <= 100 and tactical:
        return "interesting"
    if loss <= 140:
        return "inaccuracy"
    if loss <= 320:
        return "mistake"
    return "blunder"


def review_move(before, move, after, candidates, played):
    best = candidates[0]
    forced = before.legal_moves.count() == 1
    loss = 0 if forced or after.is_checkmate() else adjusted_loss(best.cp, played.cp)
    lost_mate = best.mate is not None and best.mate > 0 and (played.mate is None or played.mate < 0)
    allows_mate = played.mate is not None and played.mate < 0 and not (best.mate is not None and best.mate < 0)
    if lost_mate or allows_mate:
        loss = max(loss, 500)
    facts = evidence(before, move, after, best, played, loss)
    concepts = list(dict.fromkeys(f.concept for f in facts))
    tactical = bool(set(concepts) & {"garfo", "cravada", "ameaça de mate"})
    unique = len(candidates) >= 2 and best.move == move and best.cp - candidates[1].cp >= 160
    sacrifice = move.to_square in hanging(after, before.turn) and VALUES[after.piece_type_at(move.to_square)] >= 3
    classification = classify(loss, forced=forced, mate_found=after.is_checkmate(), mate_lost=lost_mate,
                              allows_mate=allows_mate, tactical=tactical, unique=unique, sacrifice=sacrifice)
    # An error explanation must not be displaced by a positive development fact.
    chosen = next((f for f in facts if f.negative), facts[0]) if loss > 60 else next((f for f in facts if not f.negative), facts[0])
    return {"move": before.san(move), "uci": move.uci(), "classification": classification,
            "label": LABELS[classification], "comment": chosen.text,
            "pogona_state": POSES[classification], "concepts": concepts,
            "is_forced": forced, "is_unique": unique, "loss": loss,
            "before_cp": best.cp, "after_cp": played.cp, "best_move": best.move.uci() if best.move else None,
            "evidence": [asdict(f) for f in facts]}


def accuracy(reviews):
    if not reviews:
        return None
    # Average per-move quality: bounded, monotonic, with a meaningful cost for blunders.
    return round(sum(100 * math.exp(-r["loss"] / 180) for r in reviews) / len(reviews), 1)


def public_review(review):
    return {k: v for k, v in review.items() if k not in ("loss", "before_cp", "after_cp", "best_move", "evidence")}


def summary(reviews):
    positive, negative = Counter(), Counter()
    for review in reviews:
        for fact in review["evidence"]:
            if fact["concept"] != "atividade":
                if fact["negative"]:
                    negative[fact["concept"]] += 1
                elif review["loss"] <= 100:
                    positive[fact["concept"]] += 1
    return {"accuracy": accuracy(reviews), "counts": {label: sum(r["classification"] == key for r in reviews) for key, label in LABELS.items()},
            "strengths": [k for k, _ in positive.most_common(3)], "improve": [k for k, _ in negative.most_common(3)],
            "concepts": dict((positive + negative).most_common(6)), "reviewed_moves": len(reviews)}
