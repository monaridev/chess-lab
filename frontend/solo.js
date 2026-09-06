/* Solo owns its session; multiplayer and lessons keep their existing state. */
(() => {
  "use strict";
  const el = id => document.getElementById(id);
  const KEY = "chesslab.solo.v1", SESSION = "chesslab.solo.session";
  const difficulties = {beginner: "Iniciante", easy: "Fácil", medium: "Médio", hard: "Difícil"};
  let prefs = {difficulty: "beginner", color: "white", help_mode: "progressive", gamesPlayed: 0, bestAccuracy: null, recentAccuracy: []};
  let token = null, counted = false, data = null, selected = null, busy = false, visible = false, version = 0, promotion = null;
  try {
    const stored = JSON.parse(localStorage.getItem(KEY));
    if (stored && typeof stored === "object") {
      if (Object.hasOwn(difficulties, stored.difficulty)) prefs.difficulty = stored.difficulty;
      if (["white", "black"].includes(stored.color)) prefs.color = stored.color;
      if (["review", "progressive"].includes(stored.help_mode)) prefs.help_mode = stored.help_mode;
      if (Number.isSafeInteger(stored.gamesPlayed) && stored.gamesPlayed >= 0) prefs.gamesPlayed = stored.gamesPlayed;
      if (Number.isFinite(stored.bestAccuracy) && stored.bestAccuracy >= 0 && stored.bestAccuracy <= 100) prefs.bestAccuracy = stored.bestAccuracy;
      if (Array.isArray(stored.recentAccuracy)) prefs.recentAccuracy = stored.recentAccuracy.filter(n => Number.isFinite(n) && n >= 0 && n <= 100).slice(-10);
    }
  } catch (_) { /* Corrupt/blocked storage is optional. */ }
  try {
    const session = JSON.parse(sessionStorage.getItem(SESSION));
    if (session && typeof session.token === "string" && /^[\w-]{40,60}$/.test(session.token)) { token = session.token; counted = session.counted === true; }
  } catch (_) { /* Play remains available without persistence. */ }
  function saveSession() { try { sessionStorage.setItem(SESSION, JSON.stringify({token, counted})); } catch (_) {} }
  function savePrefs() {
    try { localStorage.setItem(KEY, JSON.stringify(prefs)); el("solo-storage").textContent = "Preferências e estatísticas leves salvas neste navegador."; }
    catch (_) { el("solo-storage").textContent = "Não foi possível salvar neste navegador. Você pode continuar jogando."; }
  }
  let summaryPresented = false;
  const gradeIcons = {brilliant: "✦", excellent: "✧", very_good: "✓", good: "✓", interesting: "!", inaccuracy: "?!", mistake: "?", blunder: "×"};
  const poseLabels = {idle: "Ao seu lado", observando: "Observando", pensando: "Pensando", alerta: "Alertando", ensinando: "Ensinando", elogiando: "Elogiando", feliz: "Muito bem", comemorando: "Comemorando"};
  function closeDialogs() { el("solo").querySelectorAll("dialog[open]").forEach(dialog => dialog.close()); }
  function openDialog(id) { closeDialogs(); el(id).showModal(); }
  function moreTools(open) { el("solo-tools").classList.toggle("expanded", open); el("solo-more").setAttribute("aria-expanded", String(open)); }
  function setOption(name, value) { el("solo-form").querySelectorAll(`input[name="${name}"]`).forEach(input => { input.checked = input.value === value; }); }
  // Reuse the existing controls, theme tokens, skin assets and storage handler.
  const appearancePanel = document.createElement("div"); appearancePanel.className = "solo-appearance";
  function renderAppearance() {
    appearancePanel.replaceChildren();
    for (const [source, title, type] of [["board-theme", "Aparência do tabuleiro", "theme"], ["piece-skin", "Estilo das peças", "skin"]]) {
      const group = document.createElement("fieldset"), legend = document.createElement("legend"), options = document.createElement("div");
      group.className = "solo-visual-options"; legend.textContent = title; options.className = "solo-swatches";
      for (const option of el(source).options) {
        const button = document.createElement("button"), preview = document.createElement("span"), label = document.createElement("span");
        button.type = "button"; button.className = "solo-swatch"; button.dataset.option = option.value; button.dataset.appearance = type;
        button.setAttribute("aria-pressed", String(appearance[type] === option.value)); button.setAttribute("aria-label", option.textContent);
        preview.className = "solo-swatch-preview"; preview.setAttribute("aria-hidden", "true");
        if (type === "theme") { preview.dataset.theme = option.value; for (let i = 0; i < 9; i++) preview.append(document.createElement("i")); }
        else { const img = document.createElement("img"); img.src = `/static/pieces/${option.value === "classic" ? "" : `skins/${option.value}/`}white-n.svg`; img.alt = ""; preview.append(img); }
        label.textContent = option.textContent; button.append(preview, label);
        button.addEventListener("click", () => {
          el(source).value = option.value; el(source).dispatchEvent(new Event("change"));
          appearancePanel.querySelectorAll(`[data-appearance="${type}"]`).forEach(b => b.setAttribute("aria-pressed", String(b.dataset.option === option.value)));
          el("solo-storage").textContent = el("appearance-status").textContent;
          if (data) renderChessBoard(el("solo-board"), data.board, selected, data.reveal?.move, data.color);
        }); options.append(button);
      }
      group.append(legend, options); appearancePanel.append(group);
    }
  }
  let poseVersion = 0;
  const images = new Map();
  function pose(state, message) {
    const ticket = ++poseVersion;
    if (!images.has(state)) {
      const img = new Image(); img.src = `/static/assets/pogona/professor_pogona_${state}.png`;
      images.set(state, img.decode().then(() => img.src).catch(() => null));
    }
    images.get(state).then(src => { if (src && ticket === poseVersion) el("solo-pose").src = src; });
    el("solo-speech").textContent = message;
    el("solo-pose-label").textContent = poseLabels[state];
    el("solo-pose").alt = `Professor Pogona — ${poseLabels[state]}`;
  }
  function controls() {
    const playing = data?.board.status === "playing", ownTurn = data?.board.turn === data?.color;
    el("solo-start").disabled = busy;
    el("solo-resume").disabled = busy;
    el("solo-retry").disabled = busy;
    el("solo-board").setAttribute("aria-busy", String(busy));
    el("solo-hint").disabled = busy || !playing || !ownTurn || data?.help_mode !== "progressive" || data?.hint_level >= 4;
    el("solo-hint").textContent = data?.hint_level ? `Aprofundar dica (${data.hint_level}/4)` : "Pedir dica";
    el("solo-hint").hidden = data?.help_mode === "review";
    el("solo-reveal").hidden = !playing || data?.hint_level < 4 || Boolean(data?.reveal);
    for (const id of ["solo-reveal", "solo-reveal-yes", "solo-resign", "solo-resign-yes", "solo-new"]) el(id).disabled = busy || (id !== "solo-new" && !playing);
  }
  function render() {
    if (!data) return;
    el("solo-setup").hidden = true; el("solo-game").hidden = false;
    el("solo").dataset.screen = "game"; el("solo-tools").hidden = false; el("solo-look-open").hidden = false;
    el("solo-appearance-game").append(appearancePanel);
    const finished = data.board.status === "finished";
    el("solo-turn").textContent = finished ? "Partida concluída" : data.board.turn === data.color ? (data.board.check ? "Sua vez · seu rei está em xeque" : "Sua vez") : "Stockfish está pensando…";
    el("solo-info").textContent = `${difficulties[data.difficulty]} · Você joga de ${data.color === "white" ? "brancas" : "pretas"}`;
    renderChessBoard(el("solo-board"), data.board, selected, data.reveal?.move, data.color);
    el("solo-grade").textContent = data.review ? `${data.review.move} · ${data.review.label}${data.review.is_forced ? " · Forçada" : data.review.is_unique ? " · Única" : ""}` : "Antes do primeiro lance";
    el("solo-grade-card").hidden = !data.review;
    el("solo-grade-card").dataset.grade = data.review?.classification || "";
    el("solo-grade-icon").textContent = gradeIcons[data.review?.classification] || "✧";
    el("solo-last").textContent = data.board.last_move ? `Último movimento: ${data.board.last_move.slice(0, 2)} → ${data.board.last_move.slice(2, 4)}` : "Escolha uma peça e um destino.";
    el("solo-history-open").textContent = `Lances revisados (${data.history.length}) ↗`;
    el("solo-history-empty").hidden = data.history.length > 0;
    el("solo-history").replaceChildren();
    data.history.forEach((r, index) => {
      const li = document.createElement("li"), heading = document.createElement("strong"), comment = document.createElement("p");
      heading.textContent = `${index + 1}. ${r.move} · ${r.label}`; heading.dataset.grade = r.classification;
      comment.textContent = r.comment; li.append(heading, comment); el("solo-history").append(li);
    });
    el("solo-hints").replaceChildren();
    data.hints.forEach(text => { const li = document.createElement("li"); li.textContent = text; el("solo-hints").append(li); });
    el("solo-revealed").textContent = data.reveal ? `${data.reveal.move.slice(0, 2)} → ${data.reveal.move.slice(2, 4)}. ${data.reveal.message}` : "";
    el("solo-confirm").hidden = true; el("solo-resign-confirm").hidden = true;
    el("solo-result-open").hidden = !finished;
    if (finished) {
      const result = data.board.winner ? (data.board.winner === data.color ? "Você venceu" : "Stockfish venceu") : "Empate";
      const endings = {checkmate: "xeque-mate", stalemate: "afogamento", insufficient_material: "material insuficiente", threefold_repetition: "repetição", fivefold_repetition: "repetição", fifty_moves: "regra dos 50 lances", seventyfive_moves: "regra dos 75 lances", resignation: "desistência"};
      el("solo-result").textContent = `${result} · ${endings[data.board.termination] || "partida encerrada"}`;
      el("solo-accuracy").textContent = data.summary.accuracy === null ? "Sem lances" : `${data.summary.accuracy.toLocaleString("pt-BR")}%`;
      el("solo-counts").replaceChildren();
      Object.entries(data.summary.counts).forEach(([label, count], index) => {
        const li = document.createElement("li"), symbol = document.createElement("span"), title = document.createElement("span"), number = document.createElement("strong");
        const key = Object.keys(gradeIcons)[index]; li.dataset.grade = key;
        symbol.className = "solo-count-icon"; symbol.textContent = gradeIcons[key]; symbol.setAttribute("aria-hidden", "true");
        title.textContent = label; number.textContent = count; li.append(symbol, title, number); el("solo-counts").append(li);
      });
      el("solo-strengths").textContent = `${data.summary.strengths.join(", ") || "Ainda sem evidências suficientes"}.`;
      el("solo-improve").textContent = `${data.summary.improve.join(", ") || "Continue observando as ameaças antes de mover"}.`;
      el("solo-concepts").textContent = `Conceitos recorrentes: ${Object.entries(data.summary.concepts).map(([c, n]) => `${c} (${n})`).join(", ") || "nenhum lance revisado"}.`;
      if (!counted) {
        counted = true; prefs.gamesPlayed++;
        if (data.summary.accuracy !== null) {
          prefs.bestAccuracy = Math.max(prefs.bestAccuracy || 0, data.summary.accuracy);
          prefs.recentAccuracy = [...prefs.recentAccuracy, data.summary.accuracy].slice(-10);
        }
        saveSession(); savePrefs();
      }
      if (!summaryPresented) { summaryPresented = true; moreTools(false); openDialog("solo-summary"); }
      pose("comemorando", data.review ? data.review.comment : "Partida encerrada. Quando quiser, começamos outra.");
    } else if (data.review) pose(data.review.pogona_state, data.review.comment);
    controls();
  }
  async function api(path, body) {
    const controller = new AbortController(), timeout = setTimeout(() => controller.abort(), 12000);
    try {
      const response = await fetch(`/api/solo${path}`, {method: body ? "POST" : "GET", signal: controller.signal,
        headers: {"Content-Type": "application/json", "X-Solo-Token": token || ""}, ...(body ? {body: JSON.stringify(body)} : {})});
      const value = await response.json();
      if (!response.ok) throw new Error(value.message || "Não foi possível concluir. Atualize e tente novamente.");
      return value;
    } finally { clearTimeout(timeout); }
  }
  async function request(action, move = null) {
    if (busy) return;
    busy = true; selected = null; const ticket = ++version;
    el("solo-error").textContent = ""; el("solo-retry").hidden = true; controls();
    if (action === "move") pose("observando", "Estou conferindo seu lance e as respostas possíveis.");
    try {
      let value;
      if (action === "start") {
        const options = Object.fromEntries(new FormData(el("solo-form")));
        value = await api("", options);
        if (ticket !== version || !visible) return;
        token = value.token; counted = false; Object.assign(prefs, options); saveSession(); savePrefs();
        pose("observando", "Antes de jogar, confira seu rei, as peças em perigo e o centro.");
      } else if (action === "state") value = await api("");
      else value = await api("/action", {action, move, ply: data.board.ply, confirmed: ["reveal", "resign"].includes(action)});
      if (ticket !== version || !visible) return;
      data = value; render();
      if (action === "hint") { pose("ensinando", data.hints.at(-1)); moreTools(true); }
      if (action === "reveal") pose("ensinando", "Compare a possibilidade revelada com as pistas. Você decide quando jogar.");
      // The actual post-move board and comment paint before the opponent request.
      if (data.board.status === "playing" && data.board.turn !== data.color) {
        await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
        if (ticket !== version || !visible) return;
        const reply = await api("/action", {action: "reply", ply: data.board.ply});
        if (ticket !== version || !visible) return;
        data = reply; render();
      }
    } catch (error) {
      if (ticket !== version || !visible) return;
      el("solo-error").textContent = error instanceof TypeError || error.name === "AbortError" ? "Não foi possível falar com o servidor local. Confira se ele está ativo e atualize a partida." : error.message;
      el("solo-retry").hidden = !token;
      pose("alerta", "A partida está pausada. Confira a mensagem e tente novamente.");
    } finally { if (ticket === version) { busy = false; controls(); } }
  }
  function setup() {
    closeDialogs(); summaryPresented = false; moreTools(false);
    el("solo").dataset.screen = "setup"; el("solo-tools").hidden = true; el("solo-look-open").hidden = true;
    renderAppearance(); el("solo-appearance-home").append(appearancePanel);
    data = null; selected = null; el("solo-setup").hidden = false; el("solo-game").hidden = true;
    setOption("difficulty", prefs.difficulty); setOption("color", prefs.color); setOption("help_mode", prefs.help_mode);
    el("solo-resume").hidden = !token; el("solo-error").textContent = ""; el("solo-retry").hidden = true;
    pose("idle", "Escolha a dificuldade e vamos jogar no seu ritmo. Eu acompanho cada lance."); controls();
  }
  el("solo-open").addEventListener("click", () => {
    if (requestPending) return;
    visible = true; el("lobby").hidden = true; el("solo").hidden = false; document.body.classList.add("solo-active"); setup();
  });
  el("solo-back").addEventListener("click", () => {
    closeDialogs();
    version++; visible = false; busy = false; el("solo").hidden = true; document.body.classList.remove("solo-active");
    el("solo-promotion").close(); promotion = null; showLobby();
  });
  el("solo-form").addEventListener("submit", event => { event.preventDefault(); request("start"); });
  el("solo-resume").addEventListener("click", () => request("state"));
  el("solo-retry").addEventListener("click", () => request("state"));
  el("solo").querySelectorAll(".solo-dialog").forEach(dialog => dialog.addEventListener("close", () => {
    if (!visible || el("solo").querySelector("dialog[open]")) return;
    const activeElement = document.activeElement;
    if (activeElement === document.body || !activeElement.getClientRects().length) {
      el(data ? (data.board.status === "finished" ? "solo-result-open" : "solo-history-open") : "solo-start").focus({preventScroll: true});
    }
  }));
  el("solo").querySelectorAll("[data-close]").forEach(button => button.addEventListener("click", () => el(button.dataset.close).close()));
  el("solo-history-open").addEventListener("click", () => openDialog("solo-analysis"));
  el("solo-analysis-open").addEventListener("click", () => openDialog("solo-analysis"));
  el("solo-result-open").addEventListener("click", () => openDialog("solo-summary"));
  el("solo-look-open").addEventListener("click", () => { renderAppearance(); openDialog("solo-look"); });
  el("solo-more").addEventListener("click", () => moreTools(!el("solo-tools").classList.contains("expanded")));
  el("solo-new").addEventListener("click", setup);
  el("solo-hint").addEventListener("click", () => request("hint"));
  el("solo-reveal").addEventListener("click", () => { el("solo-confirm").hidden = false; });
  el("solo-reveal-no").addEventListener("click", () => { el("solo-confirm").hidden = true; });
  el("solo-reveal-yes").addEventListener("click", () => request("reveal"));
  el("solo-resign").addEventListener("click", () => { el("solo-resign-confirm").hidden = false; });
  el("solo-resign-no").addEventListener("click", () => { el("solo-resign-confirm").hidden = true; });
  el("solo-resign-yes").addEventListener("click", () => request("resign"));
  el("solo-board").addEventListener("click", event => {
    const square = event.target.closest(".square")?.dataset.square;
    if (!square || busy || !data || data.board.status !== "playing" || data.board.turn !== data.color) return;
    const moves = selected ? data.board.legal_moves.filter(m => m.startsWith(selected + square)) : [];
    if (moves.length) {
      if (moves.some(m => m.length === 5)) { promotion = selected + square; el("solo-promotion").showModal(); }
      else request("move", moves[0]);
      return;
    }
    const piece = piecesFromFen(data.board.fen)[square];
    if (piece && (piece === piece.toUpperCase()) === (data.color === "white")) selected = selected === square ? null : square;
    else el("solo-error").textContent = "Escolha uma peça sua e um destino destacado. Seu rei precisa ficar seguro.";
    renderChessBoard(el("solo-board"), data.board, selected, data.reveal?.move, data.color);
  });
  el("solo-promotion").addEventListener("close", () => {
    const choice = el("solo-promotion").returnValue, move = promotion; promotion = null;
    if (visible && move && ["q", "r", "b", "n"].includes(choice)) request("move", move + choice);
  });
})();
