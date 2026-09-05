# Publicação no Railway

A V1.2 usa o mesmo FastAPI para frontend, HTTP e WebSocket. O deploy não muda
regras, salas, preferências ou aparência.

## Selecionar o repositório

1. No Railway, escolha New Project → Deploy from GitHub Repository e selecione
   `monaridev/chess-lab`, branch `main`. Autorize acesso ao repositório privado
   se o GitHub App do Railway ainda não puder vê-lo.
2. Use a raiz do repositório. `railway.toml` seleciona o Dockerfile, healthcheck
   `/api/health`, uma réplica e desativa suspensão por inatividade.
3. Mantenha apenas uma região e uma réplica. Não configure workers adicionais.
4. Gere um domínio público em Networking. A aplicação usa HTTPS/WSS pelo proxy
   do Railway, sem serviço separado para frontend ou WebSocket.
5. Não sobrescreva o Start Command: o CMD da imagem chama `sh scripts/start.sh`.

Não é necessário configurar variável manualmente. Railway fornece `PORT`;
o Dockerfile define `STOCKFISH_PATH=/usr/games/stockfish`. Para desativar a
engine deliberadamente, pode sobrescrever `STOCKFISH_PATH` com valor vazio.
Não é necessário token, API key, banco de dados ou volume.

## Runtime

Comando efetivo:

```sh
exec python -m uvicorn backend.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 1 --ws-max-size 4096 --timeout-graceful-shutdown 15
```

A imagem Python 3.12 slim/bookworm está fixada por digest; `requirements.lock`
fixa as dependências diretas e transitivas do runtime validado. O pacote
`stockfish=15.1-4` do Debian inclui a engine e NNUE. Essa versão de produção
é diferente do Stockfish 19 instalado localmente em `.tools/`, que não vai
para o Git nem para a imagem. O build instala o pacote com suas bibliotecas e
licença. O processo final roda como usuário sem privilégios.

O fallback heurístico existente continua disponível se Stockfish falhar.
O healthcheck verifica o servidor; não exige que a engine opcional esteja ativa.
Atualizações do digest, lock e pacote devem ser acompanhadas de novos testes.
Os pacotes-base do Debian recebem resoluções de dependências no build; não se
promete imagem bit a bit idêntica com os repositórios apt evoluindo.

## Limite das salas em memória

Uma réplica/worker mantém todos os jogadores no mesmo processo. Reconexão
recupera a sessão enquanto esse processo e a credencial da aba existirem.
Reinícios, redeploys e falhas do processo apagam as partidas. Não há migração
de salas entre versões; publique atualizações sem partidas em andamento.
`overlapSeconds=0` evita prolongar a convivência com o deploy anterior, mas
não transforma o estado em memória em persistente. Não ative múltiplas regiões.

## Validação reproduzível

```sh
docker build -t chess-lab .
docker run --rm chess-lab python -m scripts.check_analysis --expected stockfish
docker run --rm -e STOCKFISH_PATH=/missing/stockfish chess-lab python -m scripts.check_analysis --expected heuristic
docker run --rm -e PORT=18765 -p 18765:18765 chess-lab
# Em outro terminal com requirements-dev.txt instalado:
python -m tests.smoke_network --url http://127.0.0.1:18765
# Repetir o servidor com -e STOCKFISH_PATH= para testar sem engine.
```

`.github/workflows/deploy-check.yml` constrói a imagem e valida engine,
fallback, PORT arbitrária, HTTP, dois WebSockets, reconexão e partida até mate.
Não precisa de secrets e não acessa o Railway. A suíte completa continua sendo
`python -m pytest -q`, com Chromium local conforme o README.

## Fontes

- [Configuração como código](https://docs.railway.com/config-as-code/reference)
- [PORT e healthchecks](https://docs.railway.com/deployments/healthchecks)
- [Start Command de imagens Docker](https://docs.railway.com/deployments/start-command)
- [Pacote Stockfish do Debian](https://packages.debian.org/bookworm/stockfish)
