# Rotinas de conteúdo da Faixa Oculta

Roteiro das rotinas na nuvem que alimentam o site além do boletim diário (`tools/BOLETIM.md`). A fonte de verdade é o
banco do artefato https://claude.ai/artifact/955jruTrT56VTc12DpqiPS (ferramenta ArtifactData); o site no GitHub Pages
é atualizado no fim por `tools/PUBLICAR.md`. O leitor é o Fabio, professor de biofísica na UFRJ, no Rio. Português do Brasil.

| Rotina | Quando | O que grava |
|---|---|---|
| Revista da semana | quinta, 8h23 | `semanas/<quinta de hoje>` |
| Música do mês | dia 1, 14h12 | `edicoes/AAAA-MM`, `itens/*`, `guias/*` |
| Cinema do mês | dia 1, 15h12 | `cine_edicoes/AAAA-MM`, `cine_itens/*`, `cine_guias/*` |
| Livros do mês | dia 1, 16h12 | `livro_edicoes/AAAA-MM`, `livro_itens/*`, `livro_guias/*` |
| Complemento quinzenal | dia 15, 14h12 | itens novos nas edições do mês de música e cinema |

## 0. Regras comuns
- `git -C /home/user/faixa-oculta pull origin main` antes de tudo. Data de hoje com `TZ=America/Sao_Paulo date +%F`.
- **Modelo é a edição anterior.** Antes de escrever, exporte com ArtifactData (action "list", out_dir) a coleção da
  rotina e leia o documento mais recente do mesmo tipo: os campos, as seções e o tamanho dos textos seguem o que está
  lá. Não invente campo novo; a página só desenha os que conhece.
- **Se o documento desta rodada já existir, não reescreva.** Só complete o que faltar e publique se o site estiver atrás.
- **Nada repetido.** Obra (disco, filme, série, livro) que já saiu em qualquer edição anterior não volta, a não ser num
  guia em que ela seja indispensável, e então com texto novo.
- Fatos: os briefs `tools/BRIEF_MUSICA.md`, `BRIEF_CINEMA.md` e `BRIEF_LIVROS.md` mandam. Pesquise tudo que for de
  2025–2026 ou incerto (WebSearch; páginas com WebFetch ou, se ele der erro de DNS, `curl -sL --compressed --max-time 30`
  simples). Não contorne bloqueio de site: 403, captcha ou paywall, use outra fonte. Nada inventado; o que não se
  confirmou fica de fora e vai para o relatório.
- Voz: a dos briefs. Sem travessão para apartes, sem "não é X, é Y", sem dois-pontos de revelação.
- Direitos autorais: paráfrase sempre; no máximo uma citação curta (menos de 15 palavras) por lote, com a fonte.
- Lote grande: divida por seção entre subagentes (ferramenta Agent), cada um com o brief inteiro, o caminho de saída e a
  lista de obras já publicadas; confira os JSON que voltarem antes de gravar.
- Gravação: ArtifactData "batch" em lotes de até 50, `if_version` em documento que já existe. Valide cada JSON com
  `python3 -I -m json.tool` antes.
- Nunca escreva em `data/users/`, e nunca crie, altere ou apague idas, notas ou o perfil do Radar por conta própria.
- Commits terminam com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Gosto do leitor, antes de escolher.** Leia (só leitura) o estado do leitor, juntando `data/users/me/estado` do artefato e o `estado.json` do repositório privado `fabiomg-pixel/faixa-oculta-estado` com `tools/juntar_estado.py` (passo 3b2 do PUBLICAR) (campos `avaliacoes` 👍 `up` / 👎 `down`
  e `marcas` quero/ouvi, com as chaves = ids de itens, `<guia>~<índice>` ou `nota:<dia>:<id da nota>`) e
  `perfil_leitor/interesses` (temas tirados da Agenda, do Gmail, do Drive e do Spotify). 👍 puxa mais do mesmo artista,
  gênero, diretor, autor ou tema; 👎 afasta. Avaliação vale mais que o perfil. Diga no relatório quantas avaliações leu.
- **Perfil de interesses (dia 1).** Uma vez por mês, na rotina de música, refaça `perfil_leitor/interesses`: títulos de
  eventos da Agenda Google dos próximos 45 dias, remetentes de newsletters do Gmail (60 dias, só metadados), títulos de
  arquivos recentes do Drive e, se houver pasta do computador ligada por Remote Control, nomes de pastas e arquivos.
  Grave só temas, com peso e onde usar; nunca copie conteúdo pessoal, nomes de terceiros ou textos.

## 1. Capas e players
- Filmes, séries e livros: `python3 -I tools/capas_obras.py <pasta> <lote.json>` (pôster pela Wikipedia ou iTunes, capa
  de livro pelo iTunes). Disco: iTunes Search (`https://itunes.apple.com/search?term=<artista álbum>&entity=album&country=br`),
  aceite só o resultado com mesmo artista e álbum, e troque `100x100bb` por `600x600bb` no `artworkUrl100`.
- Suba as imagens para o artefato: ferramenta Artifact, `url` do artefato, `asset: true`, `file_paths` (até 25 por
  chamada). Cada resultado traz a url do asset; grave no item `"capa": "/_blob/<id>"` e copie o arquivo para
  `$T/assets/<id>.jpg` no passo 5 do PUBLICAR. Sem capa confirmada, deixe o campo de fora (a página desenha um selo).
- Discos: `spotify_id` pelo conector Spotify (search, só álbum do mesmo artista) e `youtube_list` (playlist `OLAK5uy_`
  do álbum, conferida com o oEmbed do YouTube como no passo 3d2 do PUBLICAR). YouTube Music é o player principal, Spotify (barra compacta)
  o de reserva; Apple só como link (`apple_url`) quando não houver os outros.
- Filmes e séries: `imdb` (id `tt…`, conferido na página do IMDb ou da Wikipedia) para o botão do Stremio.

## 2. Revista da semana (quinta)
- doc_id = a data de hoje (quinta); `inicio` = quinta anterior, `fim` = ontem (quarta). Na primeira quinta (5/11/2026),
  `inicio` = 1/11, o dia seguinte ao fim da edição de domingo 1/11.
- Base: os boletins da semana (`dias`, query por `data` entre `inicio` e `fim`, manhã e noite) e as leituras ligadas a
  eles. Apure de novo os temas centrais: o que mudou até ontem, como cada lado cobriu.
- Forma (a de `semanas/2026-10-25`): `titulo`; `panorama` (3 parágrafos sobre o padrão da semana);
  `temas` (8 a 10, cada um com `id`, `editoria`, `titulo`, `linha_fina`, `resumo` [3 a 4 parágrafos], `cobertura`
  [4 a 6 veículos de perfis diferentes com `fonte`, `perfil`, `enfoque`, `url`], `vieses`, `o_que_falta`, `perguntas`
  [3 a 4], `por_que_importa`, `aprofundar` [3 a 5 livros, artigos, podcasts ou documentários reais, com `tipo`,
  `titulo`, `autor`, `ano`, `nota`, `url` quando houver]); `fora_do_radar` (4 a 6 assuntos que a cobertura ignorou,
  com `id`, `editoria`, `titulo`, `texto`, `ler` [{`fonte`, `titulo`, `url`}]).
- Cubra Brasil, Mundo, Ciência e universidades, Clima e Tecnologia; Rio quando houver.
- Faça as leituras limpas das URLs de `cobertura` que ainda não estão em `leituras` (`tools/LEITURAS.md`, tipo "noticia").
- Commit "Revista da semana de DD a DD/MM".

## 3. Música do mês (dia 1)
- doc_id `AAAA-MM`; `numero` = anterior + 1; `mes` "Novembro de 2026"; `data` = hoje.
- Perfil do Fabio: pelo conector Spotify (mais ouvidos recentes, playlists do mês) atualize `perfil` e `habitos` só com
  o que a ferramenta mostrar; se o conector falhar, repita o perfil anterior e diga isso no `fontes_perfil`.
- Seções (as da edição anterior): `radar` (lançamentos do mês anterior e do começo deste, 8 a 10), `descobertas` (discos
  de 2024–2026 que ele talvez não conheça, 8 a 10), `brasil` (4 a 6), `breve` (anunciados, 3 a 5). Dois ou três `guias`
  novos (7 discos cada, `tipo` "Seleção temática", "Gênero", "Cena" ou "Artista"), em temas que conversam com o perfil e
  ainda não foram feitos.
- `itens/<artista-album>` (slug minúsculo com hífens) com `edicao`, `secao`, `ordem` e os campos do item anterior.
- `layout` alterna seções e guias, como na edição anterior. `manchete` e `editorial` escritos por último, a partir do
  que entrou.
- Playlist do mês: conector Spotify, generate_playlist "Faixa Oculta nº N · <Mês> AAAA" com as faixas recomendadas dos
  itens, na ordem da revista; grave `playlist` {nome, url}. Se falhar, deixe de fora e registre.
- **Playlist com os discos inteiros.** Além da playlist de faixas, crie no conector Spotify (generate_playlist) "Faixa
  Oculta nº N · <Mês> AAAA · Álbuns Completos", pedindo todas as faixas de todos os discos com player, na ordem da revista
  (capa, seções, guias). O conector não deixa conferir o conteúdo: grave `playlist` {nome, url} com ela e guarde a de faixas
  em `playlist_anterior`. No site, o botão "Ouvir a edição inteira" toca os discos em sequência pelo YouTube Music e é o
  caminho garantido; ele usa os `youtube_list`, então confira que todo disco com player tem um.
- **Em profundidade.** Faça o campo `aprofundamento` da edição sobre o artista por trás da matéria de capa (ver §7).
- Commit "Música: edição de <mês>".

## 4. Cinema do mês e Livros do mês (dia 1, depois da música)
- doc_id da edição `AAAA-MM`, itens `AAAA-MM--<slug do título>`, guias `guia-cine-<slug>` / `guia-livro-<slug>`.
- Cinema, seções da edição anterior: `cartaz` (em cartaz ou estreando no Brasil), `series` (minisséries fechadas),
  `achados`, `brasil`, `pop`, `breve`; 20 a 25 itens e 2 guias. `onde` conferido no JustWatch Brasil ou equivalente na
  semana da rodada.
- Livros, seções: `lancamentos`, `brasil`, `ideias` (não ficção), `achados`; 15 a 18 itens e 2 guias. Edição brasileira,
  editora e páginas conferidas. Campo `downloads` só com cópias gratuitas autorizadas (regra no brief); nunca acervo pirata.
- Filmes e séries: `imdb` sempre que existir; a página põe "Assistir no Stremio" (abre a ficha, onde se adiciona à
  biblioteca), a versão web e "+ lista Trakt" (o Trakt sincroniza com Stremio e Nuvio).
- **Em profundidade.** `aprofundamento` da edição sobre o diretor (cinema) ou autor (livros) da matéria de capa (§7).
- Commit "Cinema: edição de <mês>" ou "Livros: edição de <mês>".

## 5. Complemento quinzenal (dia 15)
- Não cria edição. Acrescenta à edição de música do mês 5 a 8 discos lançados desde o dia 1 (seção `radar`) e à de
  cinema 3 a 5 estreias da quinzena no Brasil (seções `cartaz` ou `series`), com `ordem` seguindo a última do mês.
- Se as edições do mês ainda não existirem (alguma rotina do dia 1 falhou), faça primeiro a que faltar, pelos passos 3 e 4.
- Commit "Complemento da quinzena de <mês>".

## 6. Publicar e relatar
Siga `tools/PUBLICAR.md` inteiro (inclui a ponte com o Radar e as capas novas em `$T/assets`). Depois do push, confira
o `data/revista.json` do site. Relatório curto: o que entrou (quantos itens e guias, títulos dos guias), o que ficou sem
confirmação e por quê, e o hash do commit.

## 7. Em profundidade (música, cinema e livros, todo mês)
Um texto longo sobre o artista por trás da matéria de capa do mês: o músico ou banda, o diretor, o autor. Fica no
documento da edição (`edicoes`, `cine_edicoes` ou `livro_edicoes`), campo `aprofundamento`:
```json
{ "titulo": "...", "sobre": "nome do artista", "linha_fina": "1 ou 2 frases",
  "texto": ["4 a 6 parágrafos, 300 a 500 palavras: origem, formação, como o estilo se formou, fases da obra, onde a obra do mês entra"],
  "mais_da_obra": [ { "titulo": "obra (com o grupo, se for o caso)", "ano": "AAAA", "nota": "1 ou 2 frases" } ],
  "influenciados": [ { "artista": "...", "obra": "...", "ano": "AAAA", "como": "a ligação concreta: produziu, tocou, gravou no mesmo lugar, citou como influência numa entrevista..." } ],
  "fontes": [ { "fonte": "...", "url": "..." } ] }
```
- 5 a 7 obras em `mais_da_obra` (fora a do mês) e 4 a 6 em `influenciados`. A influência precisa de ligação documentada
  (colaboração, produção, declaração do próprio artista, crítica que a aponte); nada de "soa parecido" sem fonte.
- Pesquise: Wikipedia (`curl -sL "https://en.wikipedia.org/w/index.php?title=<Página>&action=raw"`, ou pt.), entrevistas e
  críticas. Todo fato com fonte listada; o que não se confirmou sai. Paráfrase; no máximo uma citação curta.
- Grave com ArtifactData "update" no documento da edição (com `if_version`). A página desenha o bloco depois da capa e
  põe "Em profundidade" no sumário.
