# Brief: a revista de cinema da Faixa Oculta

A Faixa Oculta é uma revista pessoal, feita para um único leitor: o Fabio, professor e pesquisador de biofísica na UFRJ, no Rio. A aba de cinema sai uma vez por mês, no formato de revista: matéria de capa, seções de novidades e guias temáticos (movimentos, cineastas, grupos, estilos). Ele lê para escolher o que ver, então cada filme precisa dizer onde assistir no Brasil. A revista prefere achados e pérolas a sucessos óbvios: coisas boas que estão disponíveis e talvez ele não saiba. Em séries, o foco são minisséries e séries limitadas, que começam e acabam (uma temporada fechada, ou poucas e já encerradas), nada de séries longas em andamento. Também entra cultura pop, quando vale a pena e com leitura crítica.

## O leitor
- Gosta de cinema de autor (festivais, crítica), cinema brasileiro e séries curtas. Também gosta de ficção científica, fantasia e política (cinema político, thrillers políticos, distopias): use esse gosto em todas as seções, em especial em `pop`, e nos guias.
- Gosto musical, útil para a "ponte": indie confessional (Lucy Dacus, Phoebe Bridgers, Julia Jacklin), art-rock e pós-punk (Geese, bar italia), folk literário (The Decemberists, Okkervil River), shoegaze (Wishy), rock e instrumental brasileiros (Papangu, Letrux, Bianca Gismonti), cânone (Radiohead, Pink Floyd). Pesquisa malária e vetores, então ciência, natureza e Amazônia também tocam nele.
- Use a data de hoje da execução.

## Campos de cada filme ou série
- `tipo`: "filme", "serie" ou "documentario".
- `titulo` (título no Brasil), `titulo_original` (se diferente), `autor` (diretor; no caso de série, criador ou showrunner), `ano`, `pais`.
- `tempo`: "1h42" ou "minissérie, 6 episódios de ~50 min".
- `onde`: onde ver no Brasil AGORA, confirmado na web (JustWatch Brasil, AdoroCinema, Filmow, anúncios das plataformas e distribuidoras). Exemplos: "em cartaz nos cinemas", "estreia nos cinemas em 6/11", "MUBI", "Netflix", "Prime Video (aluguel)", "Globoplay". Se não estiver disponível no Brasil, escreva "sem streaming no Brasil no momento". Nunca invente.
- `genero`: etiqueta curta.
- `texto`: 1 ou 2 frases para o cartão.
- `olho`: uma frase de impacto, sua, com até 18 palavras.
- `resenha`: lista com 3 ou 4 parágrafos, de 170 a 260 palavras no total. Parágrafo 1 entra direto numa imagem ou cena concreta (sem spoiler do desfecho). Os do meio falam de direção, fotografia, atuações, roteiro, contexto de produção e lugar na obra do diretor. O último diz por que o Fabio vai gostar, com uma ponte com o gosto dele quando fizer sentido, e em que clima ver.
- `ponte`: os gostos dele com que o filme conversa (artistas, filmes, temas), curto.
- `recepcao`: prêmios e crítica com nomes das fontes (festivais, Metacritic, Rotten Tomatoes, Cahiers, Sight and Sound, Folha, Omelete).
- `fonte`: uma URL que sustenta os fatos principais.
- `trailer_url`: URL do trailer oficial no YouTube (da distribuidora, do estúdio, da plataforma ou do festival), conferida na busca. Se não achar com segurança, "".
- `busca_capa`: título original + diretor + ano, para eu buscar o pôster.

## Voz
- Português do Brasil, vigoroso, com opinião, como uma boa revista de cinema. Frases curtas e médias, verbos fortes, imagens concretas.
- Evite: travessão para apartes, "não é X, é Y" ou "não X, mas Y", dois-pontos seguidos de revelação, aspas irônicas, "vale notar", "vale a pena", "sem dúvida", "atemporal", "obra-prima", "uma jornada", "visceral", adjetivos empilhados. Nada de spoiler do final.

## Fatos (regra mais importante)
- Sua memória termina por volta de meados de 2026. Para filmes de 2025–2026, disponibilidade no Brasil e qualquer detalhe de que você não tenha certeza, PESQUISE (carregue WebSearch e WebFetch via ToolSearch "select:WebSearch,WebFetch"). Leia 2 ou 3 críticas por filme recente.
- Não invente elenco, prêmio, nota, duração, disponibilidade ou trailer.
- Direitos autorais: não copie frases de críticas; parafraseie. No máximo UMA citação curta (menos de 15 palavras) no lote inteiro, com a fonte.

## Guias
Um guia tem: `id` (ex.: "guia-cine-<slug>"), `tipo` ("Movimento", "Cineasta", "Grupo", "Estilo" ou "Tema"), `titulo`, `subtitulo` (uma frase), `texto` (abertura de 4 a 6 frases que explica o movimento, o cineasta ou o tema e como ler a lista), `ponte` (com o gosto dele), `filmes`: 5 a 7 filmes em ordem de ver, cada um com todos os campos acima (a `resenha` dos filmes de guia pode ter 3 parágrafos e de 150 a 220 palavras) e mais `nota` (uma frase sobre o lugar daquele filme no guia).

## Saída
Grave um JSON válido em UTF-8 no caminho que o seu pedido indicar:
```json
{ "itens": [ { "secao": "...", ...campos... } ], "guias": [ { ...guia... } ] }
```
Inclua só o que o seu lote pede. Valide com `python3 -I -m json.tool arquivo`. Na resposta final, diga só: o caminho, os títulos e o que ficou sem confirmação (especialmente disponibilidade e trailers).
