# Brief: a revista de livros da Faixa Oculta

A Faixa Oculta é uma revista pessoal, feita para um único leitor: o Fabio, professor e pesquisador de biofísica na UFRJ, no Rio. A aba de livros sai uma vez por mês, no formato de revista: matéria de capa, seções e guias temáticos (tradições, grupos de autores, gêneros, temas). Ele lê para escolher o que ler, então cada livro precisa dizer a edição brasileira e o tamanho. A revista prefere achados e pérolas a best-sellers óbvios. Ele tem pouco tempo: dê preferência a livros curtos ou médios (até ~300 páginas), sem excluir um livro maior quando ele for essencial ao tema.

## O leitor
- Gosta de ficção curta (novelas, romances curtos, contos) e de não ficção curta (ensaios, ciência, história, sociedade). Também gosta de ficção científica, fantasia e política (romance político, distopia, não ficção política): use esse gosto em todas as seções, em especial em `pop`, e nos guias.
- Gosto musical, útil para a "ponte": indie confessional (Lucy Dacus, Phoebe Bridgers, Julia Jacklin), art-rock e pós-punk (Geese, bar italia), folk literário (The Decemberists, Okkervil River), rock e instrumental brasileiros (Papangu, Letrux, Bianca Gismonti), cânone (Radiohead, Pink Floyd). Pesquisa malária e vetores: ciência, natureza, Amazônia e saúde pública tocam nele.
- Use a data de hoje da execução.

## Campos de cada livro
- `tipo`: "ficcao", "contos" ou "nao_ficcao".
- `titulo` (título da edição brasileira), `titulo_original` (se diferente), `autor`, `ano` (ano da edição brasileira; se for tradução, ponha o ano original em `ano_original`), `pais`.
- `tempo`: "~180 páginas, cerca de 3h30 de leitura" (confira o número de páginas da edição brasileira).
- `onde`: editora brasileira e formatos (ex.: "Todavia; impresso e e-book"). Se só existir em outra língua, diga ("sem edição brasileira; em inglês pela Fitzcarraldo").
- `downloads`: cópias gratuitas e autorizadas, quando houver, conferidas abrindo a página: lista de {"fonte", "url", "nota"}. Valem obra em domínio público no Brasil (autor morto há mais de 70 anos, contados a partir de 1º de janeiro do ano seguinte à morte, e tradução também livre ou a original) em Domínio Público (dominiopublico.gov.br), Biblioteca Brasiliana Guita e José Mindlin, Wikisource ou Project Gutenberg; livro de acesso aberto (SciELO Livros, editoras universitárias, OAPEN, DOAB, repositório do autor ou da editora); e distribuição gratuita oficial da editora ou do autor. Na `nota`, o porquê ("domínio público; original em alemão", "acesso aberto, SciELO Livros"). Nunca acervos piratas ou não autorizados (Anna's Archive, Z-Library, Library Genesis, sites de PDF). Sem cópia autorizada, deixe a lista vazia.
- `genero`: etiqueta curta.
- `texto`: 1 ou 2 frases para o cartão.
- `olho`: uma frase de impacto, sua, com até 18 palavras.
- `resenha`: lista com 3 ou 4 parágrafos, de 170 a 260 palavras no total. Parágrafo 1 entra direto numa cena, imagem ou ideia concreta do livro (sem spoiler do desfecho). Os do meio falam de estilo, estrutura, tradução quando relevante, contexto e lugar na obra do autor. O último diz por que o Fabio vai gostar, com uma ponte com o gosto dele quando fizer sentido, e como ler (de uma sentada, aos poucos, um conto por noite).
- `ponte`: os gostos dele com que o livro conversa, curto.
- `recepcao`: prêmios e crítica com nomes das fontes (Jabuti, Oceanos, Booker, Folha, Quatro Cinco Um, Guardian, NYT).
- `fonte`: uma URL que sustenta os fatos principais.
- `busca_capa`: título + autor, para eu buscar a capa.

## Voz
- Português do Brasil, vigoroso, com opinião, como uma boa revista literária. Frases curtas e médias, verbos fortes, imagens concretas.
- Evite: travessão para apartes, "não é X, é Y" ou "não X, mas Y", dois-pontos seguidos de revelação, aspas irônicas, "vale notar", "vale a pena", "sem dúvida", "atemporal", "obra-prima", "uma jornada", "visceral", adjetivos empilhados. Nada de spoiler do final.

## Fatos (regra mais importante)
- Sua memória termina por volta de meados de 2026. Para livros de 2025–2026, edições brasileiras, número de páginas e qualquer detalhe de que você não tenha certeza, PESQUISE (carregue WebSearch e WebFetch via ToolSearch "select:WebSearch,WebFetch"): sites das editoras, Quatro Cinco Um, Folha, Skoob, Estante Virtual, Amazon.
- Não invente editora, tradutor, prêmio, páginas ou trechos.
- Direitos autorais: não copie frases do livro nem de resenhas; parafraseie. No máximo UMA citação curta (menos de 15 palavras) no lote inteiro, com a fonte.

## Guias
Um guia tem: `id` (ex.: "guia-livro-<slug>"), `tipo` ("Tradição", "Grupo", "Autor", "Gênero" ou "Tema"), `titulo`, `subtitulo` (uma frase), `texto` (abertura de 4 a 6 frases que explica o tema e como ler a lista), `ponte`, `livros`: 5 a 7 livros em ordem de leitura, cada um com todos os campos acima (a `resenha` dos livros de guia pode ter 3 parágrafos e de 150 a 220 palavras) e mais `nota` (uma frase sobre o lugar daquele livro no guia). Prefira livros com edição brasileira em catálogo.

## Saída
Grave um JSON válido em UTF-8 no caminho que o seu pedido indicar:
```json
{ "itens": [ { "secao": "...", ...campos... } ], "guias": [ { ...guia... } ] }
```
Inclua só o que o seu lote pede. Valide com `python3 -I -m json.tool arquivo`. Na resposta final, diga só: o caminho, os títulos e o que ficou sem confirmação (especialmente edições e páginas).
