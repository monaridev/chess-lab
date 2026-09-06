# ChessLab — Pack do Professor Pogona

Este pacote reúne os materiais do personagem **Professor Pogona** para o modo **Aprender** do ChessLab.

## Conteúdo

### ../../frontend/assets/pogona/
PNGs transparentes do personagem, prontos para uso na interface.
- `professor_pogona_idle.png` — pose base / neutra
- `professor_pogona_feliz.png` — feliz / animado
- `professor_pogona_pensando.png` — pensando
- `professor_pogona_alerta.png` — alerta / cuidado
- `professor_pogona_observando.png` — observando com binóculos
- `professor_pogona_ensinando.png` — ensinando com apontador
- `professor_pogona_elogiando.png` — elogiando / aprovação
- `professor_pogona_comemorando.png` — comemorando vitória
- `assets/asset_pack_preview.jpg` (nesta pasta de documentação) — prévia rápida das poses

### mockups/
- `chesslab_modo_aprender_mockup.png` — proposta visual de tela para o modo Aprender com o Pogona.

### concept/
Materiais de conceito e evolução visual do personagem.

### Documentação nesta pasta
- `mini_conceito_pogona.md`
- `falas_base_pogona.md`

## Uso recomendado na interface
- **Idle / padrão:** `professor_pogona_idle.png`
- **Ao pedir dica:** `professor_pogona_observando.png`
- **Explicação guiada:** `professor_pogona_ensinando.png`
- **Jogada arriscada do usuário:** `professor_pogona_alerta.png`
- **Jogada boa:** `professor_pogona_elogiando.png`
- **Lição concluída / tática achada:** `professor_pogona_comemorando.png`
- **Momento leve / recompensa:** `professor_pogona_feliz.png`
- **Perguntas de reflexão:** `professor_pogona_pensando.png`

## Observação
O personagem foi pensado para ficar **sempre visível**, mas com falas curtas e não invasivas.

## Integração

O pacote temporário foi incorporado ao projeto. Veja [IMPLEMENTACAO.md](IMPLEMENTACAO.md)
para API, currículo, progresso, estados e instruções para novas lições.
