/* Shared presentation only; legal moves and positions come from the server. */
function renderChessBoard(element, board, selected = null, revealed = null, color = "white") {
    const pieces = piecesFromFen(board.fen);
    const destinations = new Set(selected ? board.legal_moves.filter(m => m.startsWith(selected)).map(m => m.slice(2, 4)) : []);
    const fragment = document.createDocumentFragment();
    for (const rank of (color === "white" ? "87654321" : "12345678")) for (const file of (color === "white" ? "abcdefgh" : "hgfedcba")) {
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
      if (file === (color === "white" ? "a" : "h")) { const c = document.createElement("span"); c.className = "coord rank"; c.textContent = rank; c.setAttribute("aria-hidden", "true"); button.append(c); }
      if (rank === (color === "white" ? "1" : "8")) { const c = document.createElement("span"); c.className = "coord file"; c.textContent = file; c.setAttribute("aria-hidden", "true"); button.append(c); }
      fragment.append(button);
    }
    const focus = element.contains(document.activeElement) ? document.activeElement.dataset.square : null;
    element.replaceChildren(fragment);
    if (focus) element.querySelector(`[data-square="${focus}"]`)?.focus({preventScroll: true});
}
