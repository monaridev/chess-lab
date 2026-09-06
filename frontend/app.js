"use strict";

const $ = (id) => document.getElementById(id);
const SESSION_KEY = "chesslab.session.v1";
const APPEARANCE_KEY = "chesslab.appearance.v1";
const themes = ["laboratory", "matcha", "strawberry", "midnight", "lavender", "elmore", "watterson"];
const skins = ["classic", "soft", "cute", "minimal", "cartoon"];
let appearance = {theme: "laboratory", skin: "classic"};
let revealedMove = null, revealPosition = null;
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const names = {p: "peão", n: "cavalo", b: "bispo", r: "torre", q: "dama", k: "rei"};
const endings = {checkmate: "Xeque-mate", stalemate: "Afogamento", insufficient_material: "Material insuficiente", threefold_repetition: "Repetição tripla", fivefold_repetition: "Repetição quíntupla", fifty_moves: "Regra dos 50 lances", seventyfive_moves: "Regra dos 75 lances"};
let session = null, state = null, socket = null, reconnectTimer = null, retry = 0;
let selected = null, connected = false, pendingMove = false, pendingHint = false, hintLevel = 0;
let promotionIntent = null, active = false, requestPending = false;

function loadSession() {
  try {
    const saved = JSON.parse(sessionStorage.getItem(SESSION_KEY));
    if (saved && /^[A-Z2-9]{6}$/.test(saved.code) && ["white", "black"].includes(saved.color) && typeof saved.player_token === "string") return saved;
  } catch (_) { /* Armazenamento indisponível: a sessão atual ainda pode jogar. */ }
  return null;
}
function saveSession(value) {
  try {
    if (value) sessionStorage.setItem(SESSION_KEY, JSON.stringify(value));
    else sessionStorage.removeItem(SESSION_KEY);
  } catch (_) { $("game-error").textContent = "O navegador bloqueou o armazenamento. Evite recarregar esta aba durante a partida."; }
}
function setError(message) { $(active ? "game-error" : "lobby-error").textContent = message; }
function setConnection(message, online = false) {
  connected = online;
  $("connection").textContent = message;
  $("connection").classList.toggle("offline", !online);
  updateControls();
}
function canMove() { return connected && state?.status === "playing" && state.turn === session?.color && !pendingMove; }
function updateControls() {
  $("hint").disabled = !canMove() || state?.mode !== "assisted" || pendingHint || hintLevel >= 4;
  $("hint").textContent = hintLevel >= 4 ? "Dicas reveladas" : hintLevel ? "Aprofundar dica →" : "Pedir dica ✧";
  $("reveal").disabled = !canMove() || state?.mode !== "assisted" || pendingHint || Boolean(revealedMove);
  $("analysis-status").textContent = pendingHint ? "Preparando uma pista para esta posição…" : "";
  $("hint-content").setAttribute("aria-busy", String(pendingHint));
}
async function enterRoom(path, body) {
  if (requestPending) return;
  requestPending = true;
  $("create").disabled = $("join").disabled = true;
  $("lobby-error").textContent = "";
  try {
    const response = await fetch(path, {method: "POST", headers: {"Content-Type": "application/json"}, ...(body ? {body: JSON.stringify(body)} : {})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || "Não foi possível abrir a sala. Confira os dados e tente novamente.");
    session = data;
    saveSession(session);
    startGame();
  } catch (error) { $("lobby-error").textContent = error instanceof TypeError ? "Não foi possível conectar ao servidor. Confira sua conexão." : error.message; }
  finally { requestPending = false; $("create").disabled = $("join").disabled = false; }
}

function resetHints() {
  revealedMove = null;
  revealPosition = null;
  if ($("reveal-dialog").open) $("reveal-dialog").close("cancel");
  $("reveal-content").hidden = true;
  $("reveal-content").replaceChildren();
  hintLevel = 0;
  pendingHint = false;
  $("hint-content").replaceChildren();
  const p = document.createElement("p");
  p.textContent = state?.mode === "normal" ? "Esta é uma Partida Normal. Para jogar com dicas, crie uma Partida Assistida." : "Quando for sua vez, peça uma dica para explorar a posição.";
  $("hint-content").append(p);
  document.querySelectorAll(".hint-steps li").forEach((li) => li.classList.remove("revealed"));
}
function startGame() {
  active = true;
  state = null;
  selected = null;
  pendingMove = false;
  retry = 0;
  $("lobby").hidden = true;
  $("game").hidden = false;
  $("game-error").textContent = "";
  $("room-code").textContent = session.code;
  $("your-color").textContent = session.color === "white" ? "Brancas" : "Pretas";
  $("mode-label").textContent = session.mode === "assisted" ? "PARTIDA ASSISTIDA" : "PARTIDA NORMAL";
  $("board").replaceChildren();
  $("turn-label").textContent = "Preparando tabuleiro…";
  $("game-status").textContent = "";
  $("last-move").textContent = "Posição inicial";
  $("copy-status").textContent = "Compartilhe o código com seu adversário.";
  resetHints();
  connect();
}
function stopConnection() {
  clearTimeout(reconnectTimer);
  reconnectTimer = null;
  const old = socket;
  socket = null;
  if (old) old.close();
  connected = false;
  selected = null;
  pendingMove = pendingHint = false;
  promotionIntent = null;
  if ($("promotion-dialog").open) $("promotion-dialog").close("cancel");
  revealPosition = null;
  if ($("reveal-dialog").open) $("reveal-dialog").close("cancel");
}
function connect() {
  stopConnection();
  if (!active || !session) return;
  $("reconnect").hidden = true;
  setConnection(retry ? "Reconectando…" : "Conectando…");
  const current = new WebSocket(`${location.protocol === "https:" ? "wss:" : "ws:"}//${location.host}/ws/${encodeURIComponent(session.code)}`);
  socket = current;
  current.addEventListener("open", () => {
    if (socket === current) current.send(JSON.stringify({type: "auth", token: session.player_token}));
  });
  current.addEventListener("message", (event) => {
    if (socket !== current) return;
    const message = JSON.parse(event.data);
    if (message.type === "state") {
      const positionChanged = !state || state.fen !== message.fen || state.ply !== message.ply;
      const animateMove = Boolean(state && positionChanged && message.ply === state.ply + 1);
      state = message;
      retry = 0;
      pendingMove = false;
      if (positionChanged) {
        selected = null;
        promotionIntent = null;
        if ($("promotion-dialog").open) $("promotion-dialog").close("cancel");
        resetHints();
        $("game-error").textContent = "";
      }
      setConnection("Conectado", true);
      render(animateMove);
    } else if (message.type === "error") {
      if (message.ply !== undefined && message.ply !== state?.ply) return;
      pendingMove = pendingHint = false;
      setError(message.message);
      updateControls();
      if (["ROOM_NOT_FOUND", "INVALID_TOKEN"].includes(message.code)) {
        const reason = message.message;
        active = false;
        stopConnection();
        session = null;
        saveSession(null);
        showLobby();
        $("lobby-error").textContent = reason;
      }
    } else if (message.type === "hint") {
      if (message.ply !== state?.ply) return;
      pendingHint = false;
      $("hint-content").replaceChildren();
      message.messages.forEach((text, index) => {
        const p = document.createElement("p"), title = document.createElement("strong");
        title.textContent = `PISTA ${index + 1} / 4`;
        p.append(title, document.createTextNode(text));
        $("hint-content").append(p);
      });
      $("hint-content").scrollTop = $("hint-content").scrollHeight;
      hintLevel = message.level;
      document.querySelectorAll(".hint-steps li").forEach((li) => li.classList.toggle("revealed", Number(li.dataset.level) <= hintLevel));
      updateControls();
    } else if (message.type === "reveal") {
      if (message.ply !== state?.ply) return;
      pendingHint = false;
      revealedMove = message.move;
      $("reveal-content").replaceChildren();
      const title = document.createElement("strong"), explanation = document.createElement("p"), method = document.createElement("p");
      title.textContent = `${message.san} · ${message.move.slice(0, 2)} → ${message.move.slice(2, 4)}`;
      explanation.textContent = message.explanation;
      method.className = "quiet";
      method.textContent = message.source === "stockfish" ? "Possibilidade calculada com análise local." : "Possibilidade calculada por heurísticas locais, com análise limitada.";
      const legend = document.createElement("div");
      legend.className = "reveal-legend";
      ["1 · Origem", "2 · Destino"].forEach((text) => {
        const item = document.createElement("span"); item.textContent = text; legend.append(item);
      });
      $("reveal-content").append(title, legend, explanation, method);
      $("reveal-content").hidden = false;
      renderBoard();
      updateControls();
    }
  });
  current.addEventListener("close", (event) => {
    if (socket !== current || !active) return;
    selected = null;
    pendingMove = pendingHint = false;
    promotionIntent = null;
    if ($("promotion-dialog").open) $("promotion-dialog").close("cancel");
    revealPosition = null;
    if ($("reveal-dialog").open) $("reveal-dialog").close("cancel");
    setConnection("Reconectando…");
    if (state) renderBoard();
    if (event.code === 4001 || event.code === 4003) {
      setConnection("Desconectado");
      setError(event.code === 4001 ? "Sua sessão foi aberta em outra conexão. Você pode retomá-la nesta aba." : "Não foi possível identificar a sessão. Tente reconectar.");
      $("reconnect").hidden = false;
      return;
    }
    reconnectTimer = setTimeout(connect, Math.min(500 * 2 ** retry++, 5000));
  });
  current.addEventListener("error", () => { if (socket === current) setConnection("Reconectando…"); });
}
function piecesFromFen(fen) {
  const pieces = {};
  fen.split(" ")[0].split("/").forEach((row, index) => {
    let file = 0;
    for (const char of row) {
      if (/\d/.test(char)) file += Number(char);
      else { pieces[`${"abcdefgh"[file]}${8 - index}`] = char; file++; }
    }
  });
  return pieces;
}
function renderBoard(animateMove = false) {
  if (!state) return;
  const originRect = animateMove && state.last_move ? $("board").querySelector(`[data-square="${state.last_move.slice(0, 2)}"]`)?.getBoundingClientRect() : null;
  const pieces = piecesFromFen(state.fen);
  const files = session.color === "white" ? "abcdefgh" : "hgfedcba";
  const ranks = session.color === "white" ? "87654321" : "12345678";
  const destinations = new Set(selected && canMove() ? state.legal_moves.filter((m) => m.startsWith(selected)).map((m) => m.slice(2, 4)) : []);
  const fragment = document.createDocumentFragment();
  for (const [ri, rank] of [...ranks].entries()) {
    for (const [fi, file] of [...files].entries()) {
      const square = file + rank, piece = pieces[square];
      const button = document.createElement("button");
      button.type = "button";
      button.className = "square";
      button.dataset.square = square;
      button.classList.toggle("dark", ("abcdefgh".indexOf(file) + Number(rank)) % 2 === 1);
      button.classList.toggle("last", Boolean(state.last_move && [state.last_move.slice(0, 2), state.last_move.slice(2, 4)].includes(square)));
      button.classList.toggle("selected", selected === square);
      button.classList.toggle("legal", destinations.has(square));
      button.classList.toggle("check", state.check_square === square);
      button.classList.toggle("hint-square", Boolean(revealedMove && [revealedMove.slice(0, 2), revealedMove.slice(2, 4)].includes(square)));
      button.classList.toggle("hint-from", Boolean(revealedMove && revealedMove.slice(0, 2) === square));
      button.classList.toggle("hint-to", Boolean(revealedMove && revealedMove.slice(2, 4) === square));
      if (button.classList.contains("hint-square")) {
        const marker = document.createElement("span"); marker.className = "reveal-marker";
        marker.textContent = button.classList.contains("hint-from") ? "1" : "2";
        marker.setAttribute("aria-hidden", "true"); button.append(marker);
      }
      button.setAttribute("aria-pressed", String(selected === square));
      let label = `${square}, vazia`;
      if (piece) {
        const color = piece === piece.toUpperCase() ? "white" : "black";
        label = `${square}, ${names[piece.toLowerCase()]} ${color === "white" ? "das brancas" : "das pretas"}`;
        const img = document.createElement("img");
        const folder = appearance.skin === "classic" ? "" : `skins/${appearance.skin}/`;
        img.src = `/static/pieces/${folder}${color}-${piece.toLowerCase()}.svg`;
        img.alt = "";
        img.draggable = false;
        button.append(img);
      }
      if (destinations.has(square)) label += ", destino legal";
      if (state.check_square === square) label += ", xeque";
      if (button.classList.contains("hint-square")) label += button.classList.contains("hint-from") ? ", origem da possibilidade revelada" : ", destino da possibilidade revelada";
      button.setAttribute("aria-label", label);
      if (fi === 0) { const coord = document.createElement("span"); coord.className = "coord rank"; coord.textContent = rank; coord.setAttribute("aria-hidden", "true"); button.append(coord); }
      if (ri === 7) { const coord = document.createElement("span"); coord.className = "coord file"; coord.textContent = file; coord.setAttribute("aria-hidden", "true"); button.append(coord); }
      fragment.append(button);
    }
  }
  const focusSquare = document.activeElement?.dataset?.square;
  $("board").replaceChildren(fragment);
  if (originRect && !reducedMotion.matches) {
    const target = $("board").querySelector(`[data-square="${state.last_move.slice(2, 4)}"]`);
    const rect = target.getBoundingClientRect();
    target.querySelector("img")?.animate([
      {transform: `translate(${originRect.x - rect.x}px, ${originRect.y - rect.y}px)`},
      {transform: "translate(0, 0)"},
    ], {duration: 180, easing: "ease-out"});
  }
  if (focusSquare) $("board").querySelector(`[data-square="${focusSquare}"]`)?.focus({preventScroll: true});
}
function render(animateMove = false) {
  renderBoard(animateMove);
  document.querySelector(".board-heading").classList.toggle("finished", state.status === "finished");
  const opponent = session.color === "white" ? "black" : "white";
  for (const color of ["white", "black"]) {
    const player = state.players[color];
    $(`${color}-presence`).textContent = !player.joined ? "Aguardando" : player.connected ? "Online" : "Offline";
  }
  if (state.status === "waiting") {
    $("turn-label").textContent = "Aguardando segundo jogador";
    $("game-status").textContent = "Compartilhe o código para começar.";
  } else if (state.status === "finished") {
    $("turn-label").textContent = state.winner ? (state.winner === session.color ? "Você venceu!" : "O outro jogador venceu") : "Partida empatada";
    $("game-status").textContent = `${endings[state.termination] || "Fim da partida"} · ${state.result}`;
  } else {
    $("turn-label").textContent = state.turn === session.color ? "Sua vez" : "Vez do outro jogador";
    $("game-status").textContent = [state.check ? "Xeque: o rei precisa de proteção." : "", !state.players[opponent].connected ? "Adversário desconectado. A partida está salva." : ""].filter(Boolean).join(" ") || "Explore a posição. Encontre seu lance.";
  }
  $("turn-piece").className = `turn-indicator ${state.turn}`;
  $("last-move").textContent = state.last_san ? `Último lance: ${state.last_san}` : "Posição inicial";
  $("hint-intro").textContent = state.mode === "assisted" ? "Uma pista de cada vez, para você descobrir seu próximo lance." : "Partida Normal: joguem com suas próprias ideias.";
  updateControls();
}
function send(payload) {
  if (!connected || socket?.readyState !== WebSocket.OPEN) { setError("Aguarde a reconexão para continuar."); return false; }
  socket.send(JSON.stringify(payload));
  return true;
}
function sendMove(from, to, promotion = null) {
  if (send({type: "move", from, to, promotion})) { pendingMove = true; selected = null; $("game-error").textContent = ""; renderBoard(); updateControls(); }
}
$("board").addEventListener("click", (event) => {
  const square = event.target.closest(".square")?.dataset.square;
  if (!square || !state) return;
  if (!canMove()) {
    setError(!connected ? "Aguarde a reconexão para continuar." : state.status === "waiting" ? "Aguarde o segundo jogador entrar." : state.status === "finished" ? "A partida já terminou." : pendingMove ? "Aguarde a confirmação do lance." : "Agora é a vez do outro jogador.");
    return;
  }
  const candidates = selected ? state.legal_moves.filter((m) => m.startsWith(selected + square)) : [];
  if (candidates.length) {
    if (candidates.some((m) => m.length === 5)) {
      promotionIntent = {from: selected, to: square};
      $("promotion-dialog").returnValue = "cancel";
      $("promotion-dialog").showModal();
    } else sendMove(selected, square);
    return;
  }
  const piece = piecesFromFen(state.fen)[square];
  const own = piece && (piece === piece.toUpperCase() ? "white" : "black") === session.color;
  if (own) { selected = selected === square ? null : square; setError(""); }
  else setError(piece && !selected ? "Essa peça pertence ao outro jogador." : "Escolha uma peça sua ou um destino destacado. Seu rei deve ficar seguro.");
  renderBoard();
});
$("promotion-dialog").addEventListener("close", () => {
  const choice = $("promotion-dialog").returnValue, intent = promotionIntent;
  promotionIntent = null;
  if (intent && ["q", "r", "b", "n"].includes(choice) && canMove()) sendMove(intent.from, intent.to, choice);
});
$("create-form").addEventListener("submit", (event) => { event.preventDefault(); enterRoom("/api/rooms", {mode: new FormData(event.currentTarget).get("mode")}); });
$("join-form").addEventListener("submit", (event) => { event.preventDefault(); enterRoom(`/api/rooms/${encodeURIComponent($("room-input").value.trim().toUpperCase())}/join`); });
$("room-input").addEventListener("input", () => { $("room-input").value = $("room-input").value.toUpperCase().replace(/\s/g, ""); });
$("hint").addEventListener("click", () => { if (!$("hint").disabled && send({type: "hint"})) { pendingHint = true; updateControls(); } });
$("reveal").addEventListener("click", () => {
  if ($("reveal").disabled) return;
  revealPosition = {ply: state.ply, fen: state.fen};
  $("reveal-dialog").returnValue = "cancel";
  $("reveal-dialog").showModal();
});
$("reveal-dialog").addEventListener("close", () => {
  const position = revealPosition;
  revealPosition = null;
  if ($("reveal-dialog").returnValue === "confirm" && position && canMove() && position.ply === state.ply && position.fen === state.fen) {
    if (send({type: "reveal", confirmed: true, ply: position.ply})) { pendingHint = true; updateControls(); }
  }
});
document.querySelectorAll("dialog:has(form)").forEach((dialog) => {
  let closeTimer;
  function close(value) {
    if (reducedMotion.matches) { dialog.close(value); return; }
    dialog.classList.add("closing");
    clearTimeout(closeTimer);
    closeTimer = setTimeout(() => { if (dialog.open) dialog.close(value); }, 120);
  }
  dialog.querySelector("form").addEventListener("submit", (event) => { event.preventDefault(); close(event.submitter?.value || "cancel"); });
  dialog.addEventListener("cancel", (event) => { event.preventDefault(); close("cancel"); });
  dialog.addEventListener("close", () => { clearTimeout(closeTimer); dialog.classList.remove("closing"); });
});
$("copy").addEventListener("click", async () => {
  try {
    if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(session.code);
    else {
      const input = document.createElement("textarea"); input.value = session.code; input.className = "copy-helper"; document.body.append(input); input.select();
      const copied = document.execCommand("copy"); input.remove();
      if (!copied) throw new Error("copy");
    }
    $("copy-status").textContent = "Código copiado. Compartilhe com seu adversário.";
    $("copy").classList.remove("copy-success");
    requestAnimationFrame(() => $("copy").classList.add("copy-success"));
  } catch (_) { $("copy-status").textContent = `Selecione e copie o código: ${session.code}`; }
});
function showLobby() {
  active = false;
  stopConnection();
  $("game").hidden = true;
  $("lobby").hidden = false;
  $("resume-box").hidden = !session;
}
$("back").addEventListener("click", showLobby);
$("resume").addEventListener("click", startGame);
$("reconnect").addEventListener("click", () => { retry = 0; connect(); });
window.addEventListener("online", () => { if (active && !connected) connect(); });
window.addEventListener("offline", () => {
  if (!active) return;
  stopConnection();
  setConnection("Sem rede. Reconectando…");
  renderBoard();
});
window.addEventListener("pagehide", stopConnection);
window.addEventListener("pageshow", (event) => { if (event.persisted && active) connect(); });
function applyAppearance() {
  document.documentElement.dataset.theme = appearance.theme;
  document.documentElement.dataset.skin = appearance.skin;
  $("board-theme").value = appearance.theme;
  $("piece-skin").value = appearance.skin;
  const cozy = appearance.theme === "watterson";
  $("theme-name").textContent = cozy ? "WATTERSON COZY" : "ELMORE SCHOOL";
  $("theme-description").textContent = cozy ? "Seu cantinho para pensar o próximo lance." : "Pequenas descobertas, a cada jogada.";
  $("theme-note").textContent = cozy ? "Jogue. Respire. Sinta-se em casa." : "Grandes ideias começam com um pequeno lance.";
  $("hint-heading").replaceChildren();
  $("hint-heading").append(cozy ? "Jogue no" : "Observe antes", document.createElement("br"), cozy ? " seu ritmo." : " de mover.");
  if (state) renderBoard();
}
try {
  const stored = JSON.parse(localStorage.getItem(APPEARANCE_KEY));
  if (stored && themes.includes(stored.theme)) appearance.theme = stored.theme;
  if (stored && skins.includes(stored.skin)) appearance.skin = stored.skin;
} catch (_) { /* As preferências padrão também funcionam sem armazenamento. */ }
[$("board-theme"), $("piece-skin")].forEach((control) => control.addEventListener("change", () => {
  appearance = {theme: $("board-theme").value, skin: $("piece-skin").value};
  applyAppearance();
  try { localStorage.setItem(APPEARANCE_KEY, JSON.stringify(appearance)); $("appearance-status").textContent = "Seu visual foi salvo neste navegador."; }
  catch (_) { $("appearance-status").textContent = "Visual aplicado. Este navegador não permitiu salvar a preferência."; }
}));
applyAppearance();
session = loadSession();
if (session) startGame();
