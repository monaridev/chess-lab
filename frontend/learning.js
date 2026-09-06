/* Learning owns its UI and HTTP requests; multiplayer state and sockets stay in app.js. */
(() => {
  "use strict";
  const el = (id) => document.getElementById(id);
  const KEY = "chesslab.learning.v1";
  const poses = {idle: "Observando", pensando: "Pensando", alerta: "Alertando", observando: "Observando", ensinando: "Ensinando", elogiando: "Elogiando", comemorando: "Comemorando"};
  let progress = {chapters: {}}, chapters = [], current = null, lesson = null;
  let selected = null, busy = false, review = false, visible = false, generation = 0, revealed = null;
  try {
    const saved = JSON.parse(localStorage.getItem(KEY));
    if (saved && saved.chapters && typeof saved.chapters === "object" && !Array.isArray(saved.chapters)) {
      for (const [id, moves] of Object.entries(saved.chapters)) {
        if (/^[a-z]+$/.test(id) && Array.isArray(moves) && moves.length <= 32 && moves.every(m => typeof m === "string" && /^[a-h][1-8][a-h][1-8][qrbn]?$/.test(m))) progress.chapters[id] = moves;
      }
    }
  } catch (_) { /* A damaged or unavailable save never prevents learning. */ }
  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(progress)); el("learn-storage").textContent = "Progresso salvo neste navegador."; }
    catch (_) { el("learn-storage").textContent = "O navegador não permitiu salvar. Você pode continuar, mas o progresso será perdido ao recarregar."; }
  }
  // Selecting a piece or asking for help is not a move attempt.
  let introObjective = null;
  const poseImages = new Map();
  let poseVersion = 0;
  function preload(state) {
    if (!poseImages.has(state)) {
      const image = new Image();
      image.src = `/static/assets/pogona/professor_pogona_${state}.png`;
      poseImages.set(state, image.decode().then(() => image.getAttribute("src")).catch(() => null));
    }
    return poseImages.get(state);
  }
  function pose(state, message) {
    const version = ++poseVersion;
    // Keep the last loaded pose visible until the next PNG has decoded.
    preload(state).then(src => { if (src && version === poseVersion) el("pogona-pose").src = src; });
    el("pogona-pose").alt = `Professor Pogona — ${poses[state]}`;
    el("pogona-state").textContent = poses[state];
    el("pogona-speech").textContent = introObjective || message;
  }

  function presentObjective() {
    introObjective = lesson.objective;
    pose("ensinando", introObjective);
  }

  function controls() {
    el("learn-hint").disabled = busy || !lesson || lesson.complete || review || lesson.level >= 4;
    el("learn-hint").textContent = lesson?.level ? `Aprofundar dica (${lesson.level}/4)` : "Pedir dica";
    el("learn-reveal").hidden = !lesson || lesson.level < 4 || review || Boolean(revealed);
    el("learn-reveal").disabled = busy;
    el("learn-reveal-confirm").disabled = busy;
    el("learn-next").disabled = busy;
    el("learn-restart").disabled = busy;
    el("learn-board").setAttribute("aria-busy", String(busy));
  }
  async function request(action = "state", move = null) {
    if (busy || !current) return;
    if (action === "move") introObjective = null;
    busy = true;
    const ticket = ++generation, id = current;
    controls();
    el("learn-error").textContent = "";
    pose("pensando", "Vamos conferir a posição com calma.");
    const controller = new AbortController(), timeout = setTimeout(() => controller.abort(), 12000);
    try {
      const response = await fetch(`/api/learn/${id}`, {method: "POST", headers: {"Content-Type": "application/json"}, signal: controller.signal,
        body: JSON.stringify({moves: progress.chapters[id] || [], action, move, level: lesson?.level || 0})});
      const data = await response.json();
      if (ticket !== generation || !visible) return;
      if (!response.ok || data.accepted === false) throw new Error(data.message || "Não foi possível carregar esta lição. Tente recomeçar o capítulo.");
      lesson = data;
      progress.chapters[id] = data.moves;
      selected = null;
      if (action === "move") {
        review = true;
        revealed = null;
        save();
        pose(data.complete ? "comemorando" : "elogiando", data.feedback);
      } else if (action === "hint") {
        pose("ensinando", "Boa. Pedir dica também é aprender. Compare a pista com o tabuleiro.");
      } else if (action === "reveal") {
        revealed = data.reveal.move;
        pose("ensinando", "Agora experimente a possibilidade e observe o que ela muda.");
      } else {
        pose(data.complete ? "comemorando" : "observando", data.complete ? "Cada passo conta! Você pode revisitar este capítulo ou explorar outro." : "Antes de jogar, olhe seu rei e as peças em perigo.");
      }
      if (action === "state" && !data.complete) presentObjective();
      render(action);
    } catch (error) {
      if (ticket !== generation || !visible) return;
      el("learn-error").textContent = error instanceof TypeError || error.name === "AbortError" ? "Não foi possível falar com o servidor. Confira a conexão e tente novamente." : error.message;
      pose("alerta", "Vamos por partes. Confira o objetivo e tente outra vez. Você também pode pedir uma pista.");
    } finally {
      clearTimeout(timeout);
      if (ticket === generation) { busy = false; controls(); }
    }
  }
  function render(action) {
    el("learn-chapter-title").textContent = `${chapters.find(c => c.id === current)?.title || "Capítulo"} · ${Math.min(lesson.step + (review ? 0 : 1), lesson.total)}/${lesson.total}`;
    if (!review) {
      el("learn-title").textContent = lesson.complete ? "Capítulo concluído" : lesson.title;
      el("learn-objective").textContent = lesson.complete ? "Boa! Você observou, testou e aprendeu. Continue explorando ou pratique de novo." : lesson.objective;
    }
    el("learn-feedback").textContent = review ? lesson.feedback : "";
    el("learn-next").hidden = !review && !lesson.complete;
    el("learn-next").textContent = lesson.complete ? "Voltar aos capítulos →" : "Próxima lição →";
    if (action !== "reveal") {
      el("learn-hints").replaceChildren();
      (lesson.hints || []).forEach((text, index) => { const li = document.createElement("li"); li.textContent = `Pista ${index + 1}: ${text}`; el("learn-hints").append(li); });
      el("learn-revealed").textContent = "";
    }
    if (lesson.reveal) el("learn-revealed").textContent = lesson.reveal.message;
    el("learn-confirm").hidden = true;
    renderBoard();
  }
  function renderBoard() {
    if (!lesson) return;
    const board = review && lesson.after ? lesson.after : lesson.board;
    const pieces = piecesFromFen(board.fen);
    const destinations = new Set(selected ? board.legal_moves.filter(m => m.startsWith(selected)).map(m => m.slice(2, 4)) : []);
    const fragment = document.createDocumentFragment();
    for (const rank of "87654321") for (const file of "abcdefgh") {
      const square = file + rank, piece = pieces[square], button = document.createElement("button");
      button.type = "button"; button.className = "square"; button.dataset.square = square;
      button.classList.toggle("dark", ("abcdefgh".indexOf(file) + Number(rank)) % 2 === 1);
      button.classList.toggle("selected", square === selected);
      button.classList.toggle("legal", destinations.has(square));
      button.classList.toggle("check", board.check_square === square);
      button.classList.toggle("last", Boolean(board.last_move && [board.last_move.slice(0, 2), board.last_move.slice(2, 4)].includes(square)));
      button.classList.toggle("hint-from", revealed?.slice(0, 2) === square);
      button.classList.toggle("hint-to", revealed?.slice(2, 4) === square);
      button.classList.toggle("hint-square", Boolean(revealed && [revealed.slice(0, 2), revealed.slice(2, 4)].includes(square)));
      let label = `${square}, vazia`;
      if (piece) {
        const color = piece === piece.toUpperCase() ? "white" : "black", img = document.createElement("img");
        img.src = `/static/pieces/${appearance.skin === "classic" ? "" : `skins/${appearance.skin}/`}${color}-${piece.toLowerCase()}.svg`;
        img.alt = ""; img.draggable = false; button.append(img);
        label = `${square}, ${names[piece.toLowerCase()]} ${color === "white" ? "das brancas" : "das pretas"}`;
      }
      if (destinations.has(square)) label += ", destino legal";
      if (board.check_square === square) label += ", xeque";
      if (revealed?.slice(0, 2) === square) label += ", origem revelada";
      if (revealed?.slice(2, 4) === square) label += ", destino revelado";
      button.setAttribute("aria-label", label); button.setAttribute("aria-pressed", String(square === selected));
      if (file === "a") { const c = document.createElement("span"); c.className = "coord rank"; c.textContent = rank; c.setAttribute("aria-hidden", "true"); button.append(c); }
      if (rank === "1") { const c = document.createElement("span"); c.className = "coord file"; c.textContent = file; c.setAttribute("aria-hidden", "true"); button.append(c); }
      fragment.append(button);
    }
    const focus = el("learn-board").contains(document.activeElement) ? document.activeElement.dataset.square : null;
    el("learn-board").replaceChildren(fragment);
    if (focus) el("learn-board").querySelector(`[data-square="${focus}"]`)?.focus({preventScroll: true});
  }
  function showCatalog() {
    introObjective = null;
    generation++; busy = false; current = null; lesson = null; review = false; selected = null; revealed = null;
    el("learn-home").hidden = false; el("learn-lesson").hidden = true; el("learn-chapters").hidden = true;
    el("learn-error").textContent = ""; el("learn-catalog").replaceChildren();
    let completed = 0;
    chapters.forEach((chapter, index) => {
      const count = Math.min(progress.chapters[chapter.id]?.length || 0, chapter.total);
      if (count === chapter.total) completed++;
      const button = document.createElement("button"); button.className = "learn-card panel"; button.dataset.chapter = chapter.id;
      const number = document.createElement("span"), title = document.createElement("strong"), status = document.createElement("small");
      number.className = "eyebrow"; number.textContent = `CAPÍTULO ${index + 1}`; title.textContent = chapter.title;
      status.textContent = `${count}/${chapter.total} lições · ${count === chapter.total ? "Concluído · Revisitar" : count ? "Continuar" : "Começar"}`;
      button.append(number, title, status); button.addEventListener("click", () => openChapter(chapter.id)); el("learn-catalog").append(button);
    });
    el("learn-progress").textContent = `${completed} de ${chapters.length} capítulos concluídos`;
    pose("idle", "Oi! Eu sou o Professor Pogona. Escolha um capítulo e vamos aprender no seu ritmo.");
    el("learn-scroll").scrollTop = 0;
  }
  function openChapter(id) {
    introObjective = null;
    generation++; busy = false; current = id; lesson = null; review = false; selected = null; revealed = null;
    el("learn-home").hidden = true; el("learn-lesson").hidden = false; el("learn-chapters").hidden = false;
    el("learn-board").replaceChildren(); el("learn-title").textContent = "Preparando lição…";
    el("learn-objective").textContent = ""; el("learn-feedback").textContent = ""; el("learn-hints").replaceChildren(); el("learn-revealed").textContent = "";
    el("learn-next").hidden = true; el("learn-confirm").hidden = true;
    el("learn-scroll").scrollTop = 0;
    request();
  }
  el("learn-open").addEventListener("click", async () => {
    if (requestPending) return;
    Object.keys(poses).forEach(preload);
    visible = true; el("lobby").hidden = true; el("learning").hidden = false; document.body.classList.add("learning-active");
    showCatalog();
    const ticket = generation;
    try {
      const response = await fetch("/api/learn");
      if (!response.ok) throw new Error();
      const data = await response.json();
      if (!visible || ticket !== generation) return;
      chapters = data; showCatalog();
    } catch (_) { if (visible && ticket === generation) { el("learn-error").textContent = "Não foi possível carregar os capítulos. Volte ao início e tente novamente."; pose("alerta", "Confira sua conexão. Vamos tentar de novo."); } }
  });
  el("learn-back").addEventListener("click", () => { generation++; busy = false; visible = false; el("learning").hidden = true; el("learn-board").replaceChildren(); document.body.classList.remove("learning-active"); showLobby(); el("learn-open").focus(); });
  el("learn-chapters").addEventListener("click", showCatalog);
  el("learn-restart").addEventListener("click", () => { if (busy) return; progress.chapters[current] = []; save(); openChapter(current); });
  el("learn-next").addEventListener("click", () => {
    if (lesson.complete) { showCatalog(); return; }
    review = false; selected = null; revealed = null; render("state"); controls();
    presentObjective();
    el("learn-title").focus();
  });
  el("learn-board").addEventListener("click", event => {
    const square = event.target.closest(".square")?.dataset.square;
    if (!square || !lesson || busy || review || lesson.complete) return;
    const candidate = selected && lesson.board.legal_moves.find(m => m === selected + square || m === selected + square + "q");
    if (candidate) { request("move", candidate); return; }
    const piece = piecesFromFen(lesson.board.fen)[square];
    if (piece && piece === piece.toUpperCase()) {
      selected = selected === square ? null : square; el("learn-error").textContent = "";
      pose("observando", "O que muda se essa peça sair daqui? Confira os destinos destacados.");
    } else {
      if (selected) introObjective = null;
      el("learn-error").textContent = piece && !selected ? "Essa peça pertence ao outro jogador." : "Escolha uma peça branca e um destino destacado. Seu rei deve ficar seguro.";
      pose("alerta", "Pense com calma. Nem todo destino é permitido: observe o movimento da peça e a segurança do rei.");
    }
    renderBoard();
  });
  el("learn-hint").addEventListener("click", () => request("hint"));
  el("learn-reveal").addEventListener("click", () => { el("learn-confirm").hidden = false; el("learn-reveal-confirm").focus(); });
  el("learn-reveal-cancel").addEventListener("click", () => { el("learn-confirm").hidden = true; el("learn-reveal").focus(); });
  el("learn-reveal-confirm").addEventListener("click", () => request("reveal"));
})();
