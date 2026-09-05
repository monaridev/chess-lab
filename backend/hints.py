"""Tradução de evidências do tabuleiro em pistas, separada da revelação."""

from dataclasses import dataclass
import chess

VALUES = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
NAMES = {chess.PAWN: "peão", chess.KNIGHT: "cavalo", chess.BISHOP: "bispo", chess.ROOK: "torre", chess.QUEEN: "dama", chess.KING: "rei"}


def score_move(board: chess.Board, move: chess.Move) -> float:
    color = board.turn
    piece = board.piece_at(move.from_square)
    victim = board.piece_at(move.to_square)
    score = VALUES[victim.piece_type] * 10 if victim else (10 if board.is_en_passant(move) else 0)
    if board.is_castling(move):
        score += 5
    if piece.piece_type in (chess.KNIGHT, chess.BISHOP) and chess.square_rank(move.from_square) == (0 if color else 7):
        score += 3
    score += (3.5 - abs(3.5 - chess.square_file(move.to_square))) * 0.25
    if move.promotion:
        score += (VALUES[move.promotion] - 1) * 10
    after = board.copy(stack=False)
    after.push(move)
    if after.is_checkmate():
        return 10000
    if after.is_check():
        score += 1
    # Penaliza material que pode ser capturado legalmente na resposta.
    worst_loss = 0
    for reply in after.legal_moves:
        if after.gives_check(reply):
            probe = after.copy(stack=False)
            probe.push(reply)
            if probe.is_checkmate():
                return -10000
        captured = after.piece_at(reply.to_square)
        if captured and after.is_capture(reply):
            loss = VALUES[captured.piece_type]
            probe = after.copy(stack=False)
            attacker = after.piece_at(reply.from_square)
            probe.push(reply)
            if any(r.to_square == reply.to_square for r in probe.legal_moves):
                loss -= VALUES[attacker.piece_type]
            worst_loss = max(worst_loss, loss)
    return score - worst_loss * 10


@dataclass(frozen=True)
class HintPlan:
    messages: tuple[str, ...]
    move: str
    san: str
    explanation: str
    source: str
    concept: str


def describe(board: chess.Board, square: chess.Square) -> str:
    return f"{NAMES[board.piece_at(square).piece_type]} em {chess.square_name(square)}"


def build_plan(board: chess.Board, move: chess.Move | None = None, source: str = "heuristic") -> HintPlan:
    if move is None or move not in board.legal_moves:
        move = max(sorted(board.legal_moves, key=lambda m: m.uci()), key=lambda m: score_move(board, m))
        source = "heuristic"
    piece = board.piece_at(move.from_square)
    own_piece = f"{'sua' if piece.piece_type in (chess.ROOK, chess.QUEEN) else 'seu'} {NAMES[piece.piece_type]}"
    origin = chess.square_name(move.from_square)
    region = f"Olhe mais perto: {own_piece} em {origin} pode participar dessa ideia."
    after = board.copy(stack=False)
    after.push(move)
    enemy = not board.turn
    central_targets = after.attacks(move.to_square) & chess.SquareSet([chess.D4, chess.E4, chess.D5, chess.E5])
    targets = sorted([s for s in after.attacks(move.to_square)
                      if after.color_at(s) == enemy and after.piece_type_at(s) != chess.PAWN],
                     key=lambda s: 100 if after.piece_type_at(s) == chess.KING else VALUES[after.piece_type_at(s)], reverse=True)
    pinned = [s for s in targets if after.is_pinned(enemy, s) and not board.is_pinned(enemy, s)]
    attackers = board.attackers(enemy, move.from_square)
    if board.is_check():
        checkers = ", ".join(f"{NAMES[board.piece_type_at(s)]} na coluna {chess.FILE_NAMES[chess.square_file(s)]}" for s in board.checkers())
        observation = f"Seu rei em {chess.square_name(board.king(board.turn))} está em xeque. Antes de atacar, resolva a ameaça."
        concept = f"O ataque vem de {checkers}. Fugir com o rei, capturar o atacante ou bloquear a linha são as respostas possíveis; em xeque duplo, só o rei pode se mover."
        goal = "Procure uma casa segura para o rei." if piece.piece_type == chess.KING else "Procure interceptar esse ataque sem deixar outra linha aberta até seu rei."
        topic = "sair do xeque"
    elif after.is_checkmate():
        observation = "O rei adversário tem poucas saídas: existe uma oportunidade de encerrar o ataque."
        concept = "Uma rede de mate combina xeque com o controle das fugas. Confira também se o atacante pode ser capturado ou se o xeque pode ser bloqueado."
        goal = f"Procure um xeque com {own_piece} que feche todas as respostas do rei."
        topic = "rede de mate"
    elif move.promotion:
        observation = "Um peão avançado está perto de transformar o equilíbrio de forças."
        concept = "Ao chegar à última fileira, o peão vira dama, torre, bispo ou cavalo. Compare a força da nova peça e verifique se ela deixaria o adversário sem lances, causando afogamento."
        goal = "Pense em completar o avanço desse peão e escolher uma peça útil para a posição."
        topic = "promoção"
    elif len(targets) >= 2 and piece.piece_type in (chess.KNIGHT, chess.PAWN) and not after.is_pinned(board.turn, move.to_square):
        observation = "Há uma oportunidade de criar duas ameaças com uma única peça."
        target_names = " e ".join(describe(after, s) for s in targets[:2])
        concept = f"Um garfo ataca dois alvos ao mesmo tempo. Aqui, {target_names} podem ficar sob ataque; imagine qual ameaça o adversário conseguiria resolver primeiro."
        goal = f"Busque uma casa de onde {own_piece} ataque esses dois alvos. Confira se a peça sobreviveria à resposta."
        topic = "garfo"
    elif pinned:
        observation = "O alinhamento entre uma peça adversária e o rei pode ser explorado."
        concept = f"Uma cravada impede uma peça de sair da linha sem expor seu rei. A peça adversária, {describe(after, pinned[0])}, pode ficar presa a essa defesa."
        goal = f"Procure alinhar {own_piece} com essa peça e o rei atrás dela."
        topic = "cravada"
    elif board.is_en_passant(move):
        observation = "O avanço duplo de um peão adversário deixou uma oportunidade que dura só este turno."
        concept = "Na captura en passant, seu peão captura o peão que acabou de passar ao lado, como se ele tivesse avançado uma casa. É preciso verificar se a retirada dos dois peões abriria um ataque ao rei."
        goal = "Examine a captura especial disponível para seu peão antes de escolher outro plano."
        topic = "en passant"
    elif board.is_capture(move):
        victim = chess.PAWN if board.is_en_passant(move) else board.piece_type_at(move.to_square)
        defenders = len(board.attackers(enemy, move.to_square))
        defended = bool(defenders)
        observation = f"Há uma captura de {NAMES[victim]} a examinar. Antes de decidir, compare o valor das peças envolvidas."
        concept = (f"{own_piece.capitalize()} pode capturar {'uma' if victim in (chess.ROOK, chess.QUEEN) else 'um'} {NAMES[victim]}. "
                   + (f"O alvo tem {defenders} {"defensor direto" if defenders == 1 else "defensores diretos"}. Confira quais podem recapturar legalmente antes de somar o material." if defended else "O alvo não tem defesa direta, mas confira as ameaças que o adversário criaria em resposta."))
        goal = "Compare o material ganho com o que você deixaria exposto ao fazer essa captura."
        topic = "troca de material" if defended else "peça sem defesa"
    elif attackers and not after.is_attacked_by(enemy, move.to_square):
        attacker = describe(board, next(iter(attackers)))
        observation = "Uma peça sua está sob ataque e pode buscar uma posição mais segura."
        concept = f"O ataque a {own_piece} vem de {attacker}. Recuar não é perder tempo quando preserva material; procure manter a peça ativa depois da defesa."
        goal = "Busque uma casa fora desse ataque, de preferência apoiada por outra peça sua."
        topic = "defesa de peça"
    elif board.is_castling(move):
        observation = "Seu rei e uma torre ainda podem cooperar para melhorar a segurança."
        concept = "O roque retira o rei do centro e ativa a torre em um único lance. O caminho deve estar livre e o rei não pode atravessar casas atacadas."
        goal = "Confira de qual lado seu rei encontrará abrigo sem atravessar um ataque."
        topic = "segurança do rei"
    elif piece.piece_type in (chess.KNIGHT, chess.BISHOP) and chess.square_rank(move.from_square) == (0 if board.turn else 7):
        home_rank = 0 if board.turn else 7
        undeveloped = sum(1 for sq, p in board.piece_map().items()
                          if p.color == board.turn and p.piece_type in (chess.KNIGHT, chess.BISHOP)
                          and chess.square_rank(sq) == home_rank)
        observation = f"Você ainda tem {undeveloped} {"peça menor" if undeveloped == 1 else "peças menores"} na primeira fileira. Compare como elas podem participar do jogo."
        concept = f"Desenvolver {own_piece} tira uma peça da primeira fileira. "
        concept += ("Uma saída permite controlar " + ", ".join(chess.square_name(sq) for sq in central_targets) + ": são pontos de apoio no centro." if central_targets else "Compare as saídas que criam linhas de ação e ajudam a preparar a segurança do rei.")
        goal = "Compare as casas de desenvolvimento: quais controlam o centro sem oferecer a peça?"
        topic = "desenvolvimento"
    elif piece.piece_type == chess.PAWN and (chess.square_file(move.to_square) in (3, 4) or central_targets):
        opened = [describe(board, s) for s, p in board.piece_map().items()
                  if p.color == board.turn and p.piece_type in (chess.BISHOP, chess.QUEEN)
                  and len(after.attacks(s)) > len(board.attacks(s))]
        observation = "O centro pode receber mais apoio, abrindo espaço para suas peças."
        concept = "Peões disputam espaço e dão pontos de apoio às peças. "
        if central_targets:
            concept += "Uma alternativa passa a controlar " + ", ".join(chess.square_name(sq) for sq in central_targets) + " no centro. "
        concept += ("Este avanço também abre novas linhas para " + " e ".join(opened) + "." if opened else "Compare o espaço conquistado com as casas que deixariam de ser defendidas pelo peão.")
        goal = "Compare os avanços desse peão que ajudam a disputar o centro sem deixá-lo sem apoio."
        topic = "centro e espaço"
    elif piece.piece_type == chess.ROOK and not any(after.pieces(chess.PAWN, board.turn) & chess.SquareSet(chess.BB_FILES[chess.square_file(move.to_square)])):
        observation = "Uma coluna sem peões seus pode dar mais espaço a uma torre."
        concept = "Torres ganham alcance em colunas abertas ou semiabertas. O importante é ter alvos ou casas de entrada, sem esquecer a defesa da última fileira."
        goal = "Compare as colunas acessíveis a essa torre e escolha uma linha com menos bloqueios."
        topic = "controle de coluna"
    elif after.is_check():
        observation = "Uma ação com tempo pode obrigar o adversário a responder ao seu ataque."
        concept = "Um xeque força a defesa do rei, mas não é bom só por ser xeque. Compare a posição da peça atacante depois da resposta e as novas linhas abertas."
        goal = f"Examine os xeques possíveis com {own_piece} e o que cada um deixa preparado."
        topic = "iniciativa com xeque"
    elif targets and not after.is_attacked_by(enemy, move.to_square):
        observation = "Uma peça adversária pode ser pressionada sem deixar sua peça diretamente sob ataque."
        concept = f"{describe(after, targets[0]).capitalize()} pode se tornar um alvo. Atacar com segurança cria uma pergunta para o adversário: mover, defender ou contra-atacar?"
        goal = f"Compare as casas de onde {own_piece} alcança esse alvo e confira as respostas possíveis."
        topic = "pressão sobre uma peça"
    else:
        reach_before = len(board.attacks(move.from_square))
        reach_after = len(after.attacks(move.to_square))
        observation = "Há espaço para reposicionar uma peça e melhorar a coordenação."
        concept = f"{own_piece.capitalize()} influencia {reach_before} casas agora. "
        concept += (f"Uma alternativa amplia essa influência para {reach_after}; alcance precisa vir junto de segurança." if reach_after > reach_before else "Compare a qualidade das casas controladas, não só a quantidade: apoio ao centro e proteção das outras peças também contam.")
        goal = f"Procure uma posição mais útil para {own_piece}, conferindo os ataques que a mudança permite ao adversário."
        topic = "atividade e coordenação"
    san = board.san(move)
    reasons = {
        "sair do xeque": "Esse lance resolve o ataque ao seu rei e deixa uma posição legal para continuar a partida.",
        "rede de mate": "A peça dá xeque e o adversário não tem resposta legal: é xeque-mate.",
        "promoção": f"Promover a {NAMES.get(move.promotion, 'uma nova peça')} transforma o peão em uma peça com novas possibilidades de ataque e defesa.",
        "garfo": "A peça passa a atacar dois alvos ao mesmo tempo, obrigando o adversário a escolher como responder.",
        "cravada": "A nova linha de ataque prende uma peça adversária à defesa do rei, restringindo seus movimentos.",
        "en passant": "A captura aproveita a oportunidade aberta pelo avanço duplo e retira o peão adversário sem expor seu rei.",
        "troca de material": "O lance inicia uma troca de material; a análise considera a posição que fica após a captura e as respostas possíveis.",
        "peça sem defesa": "O lance captura material sem defesa direta; ainda é preciso acompanhar as ameaças da resposta adversária.",
        "defesa de peça": "A peça sai do ataque identificado e não fica diretamente atacada na nova casa.",
        "segurança do rei": "O roque afasta seu rei do centro e traz a torre para uma posição mais ativa.",
        "desenvolvimento": f"O {NAMES[piece.piece_type]} sai da primeira fileira e passa a influenciar novas casas, ajudando a coordenação das suas peças.",
        "controle de coluna": "A torre passa a atuar em uma coluna sem peões seus bloqueando a linha, ampliando suas possibilidades de entrada.",
        "iniciativa com xeque": "Esse xeque obriga o adversário a responder ao ataque ao rei antes de continuar seu plano.",
        "pressão sobre uma peça": f"A peça passa a pressionar {describe(after, targets[0]) if targets else 'alvo'}, sem ficar diretamente sob ataque na nova casa. O adversário ainda pode defender ou criar outra ameaça.",
        "atividade e coordenação": f"A peça passa a influenciar {len(after.attacks(move.to_square))} casas a partir de sua nova posição; o objetivo é melhorar a coordenação.",
    }
    explanation = concept if topic == "centro e espaço" else reasons[topic]
    if topic in ("troca de material", "peça sem defesa"):
        explanation = f"{own_piece.capitalize()} captura {'a' if board.piece_type_at(move.to_square) in (chess.ROOK, chess.QUEEN) else 'o'} {NAMES[board.piece_type_at(move.to_square)]} em {chess.square_name(move.to_square)}. " + explanation
    explanation += " Esta é uma possibilidade calculada; outras jogadas podem existir."
    return HintPlan((observation, region, concept, goal), move.uci(), san, explanation, source, topic)


def hint_messages(board: chess.Board) -> tuple[list[str], str]:
    """Compatibilidade interna para verificações das heurísticas da V1."""
    plan = build_plan(board)
    return list(plan.messages), plan.move
