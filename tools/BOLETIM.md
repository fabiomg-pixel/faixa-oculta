# Boletim diário da Faixa Oculta

Roteiro da rotina na nuvem que roda todo dia de manhã. O boletim é o documento `dias/<AAAA-MM-DD>` do artefato
https://claude.ai/artifact/955jruTrT56VTc12DpqiPS (a fonte de verdade); depois o site no GitHub Pages é atualizado.

O leitor é o Fabio, professor de biofísica na UFRJ, no Rio. Português do Brasil.

## 0. Duas edições por dia
- **Manhã** (rotina das 5h47): doc_id `AAAA-MM-DD`, campo `"edicao": "manha"`. O que aconteceu desde a noite anterior e o que
  vem no dia. 7 a 10 notas.
- **Noite** (rotina das 17h47): doc_id `AAAA-MM-DD-noite`, campo `"edicao": "noite"`, mesmo `data` do dia. O que mudou
  durante o dia: fechamento do mercado, decisões, falas, desdobramentos das notas da manhã. 4 a 7 notas, sem repetir
  nota da manhã que não teve novidade. Leia o boletim da manhã antes de apurar.
- A página mostra as duas edições do dia, a da noite primeiro ("Boletim da noite").

## 1. Ver o que já existe
- `date` com TZ=America/Sao_Paulo dá a data de hoje (base do doc_id).
- ArtifactData action "query", collection `dias`, query {"limit": 3, "order_by": {"field": "data", "direction": "desc"}},
  com out_dir. Se a edição desta rodada já existir, não reescreva: pule para o passo 4 só se o site estiver atrás.
- Leia as edições anteriores para continuar as histórias e não repetir notas sem novidade.

## 2. Apurar
- Use WebSearch (mode "extended" para os temas centrais, "standard" para checagens) para achar as matérias e
  WebFetch para abrir as principais e conferir números e falas. Se o WebFetch der erro de DNS (já aconteceu nesta
  nuvem), abra com `curl -sL --max-time 30 URL` simples, uma URL por vez, e confira o link canônico da página baixada.
  Não contorne bloqueios de site (nada de User-Agent falso nem truques): se um veículo responder 403, captcha ou
  paywall, use outro.
- Cubra, nesta ordem de peso: Brasil (política, economia), Mundo, Ciência e universidades, Clima, Tecnologia.
  Rio de Janeiro quando houver algo relevante para quem mora lá.
- Cada fato precisa de fonte. Números, nomes e datas só entram se aparecerem numa fonte; quando as fontes divergem,
  diga isso ou use o número mais conservador. Se um número é de antes de um evento (pré-mercado, apuração parcial),
  diga isso no texto.
- **Grandes veículos primeiro.** Cada nota tem 3 a 5 fontes, e pelo menos 3 delas da lista abaixo, sempre que o
  fato tiver sido coberto por eles. Portais regionais, blogs e reproduções só entram para completar, nunca no lugar.
  - Brasil: g1, Folha de S.Paulo, Estadão, O Globo, Valor Econômico, CNN Brasil, BBC News Brasil, Agência Brasil,
    Metrópoles, Veja, Gazeta do Povo (à direita), CartaCapital (à esquerda).
  - Mundo: BBC, The Guardian, Al Jazeera, DW, Le Monde, CNN, AP e Reuters (via republicação quando o site bloquear).
  - Como achar: além do WebSearch (que não indexa Estadão, BBC e Guardian), baixe com curl simples a página de seção
    do veículo (ex.: `https://g1.globo.com/politica/`, `https://www1.folha.uol.com.br/poder/`,
    `https://www.estadao.com.br/politica/`, `https://oglobo.globo.com/politica/`, `https://www.cnnbrasil.com.br/politica/`,
    `https://www.theguardian.com/world`) e procure os links do assunto com grep. A Folha e O Globo costumam fechar o
    texto: use o que a página mostrar (título, linha fina, primeiros parágrafos) e diga isso no `enfoque`.
- Cada fonte leva `enfoque`: o que aquele veículo destacou, que palavras escolheu (fuga, saída, viagem...) e quem ouviu.
- **Atualize antes de publicar.** Notícia em movimento muda em horas: confira a matéria mais recente de pelo menos dois
  grandes veículos logo antes de gravar, e corrija a nota se a versão mudou.

## 3. Escrever o documento
Confira nas páginas abertas os números e as falas de cada nota antes de gravar; o que só aparece em resumo de busca
vai atribuído ao veículo ("segundo a Reuters...").

```json
{
 "data": "AAAA-MM-DD",
 "edicao": "manha ou noite",
 "titulo": "manchete do dia, até ~70 caracteres",
 "resumo_dia": "4 a 7 frases curtas com o essencial",
 "notas": [
  {
   "id": "slug-curto",
   "editoria": "Política | Economia | Mundo | Ciência | Clima | Tecnologia | Rio | Cultura",
   "titulo": "título da nota",
   "texto": "90 a 160 palavras, só fatos com fonte",
   "como_noticiaram": "60 a 120 palavras: como os veículos contaram o mesmo fato. Onde concordam, onde divergem (números, versões, palavras escolhidas, quem foi ouvido), o que só um deles trouxe. Nomeie os veículos.",
   "analise": "50 a 100 palavras: a leitura da Faixa Oculta. O que o fato significa, o que ainda não se sabe, o que observar. Opinião fundamentada nos fatos da nota, sem adjetivo de torcida e sem fato novo sem fonte.",
   "por_que_importa": "1 ou 2 frases",
   "fontes": [ { "fonte": "Veículo", "perfil": "ex.: jornal de referência, centro", "enfoque": "o que destacou", "url": "https://..." } ]
  }
 ],
 "agenda": [ { "quando": "hoje, 10h", "o_que": "o que acontece" } ]
}
```
- Toda nota tem `como_noticiaram` e `analise`. Se só um veículo cobriu o fato, diga isso em `como_noticiaram`.
- Notas: 7 a 10 de manhã, 4 a 7 à noite. Agenda com 4 a 6 itens dos próximos dias e semanas.
- Voz: clara e direta, frases curtas. Evite travessão para apartes, "não é X, é Y", dois-pontos seguidos de revelação,
  "vale notar", "sem dúvida". Paráfrase sempre; nada copiado das fontes.
- Valide o JSON com python3 e grave com ArtifactData action "set", collection `dias`, doc_id da edição, file_path.

## 3b. Primeiras páginas (só na edição da manhã)
- Rode `python3 -I tools/capas_dia.py --data AAAA-MM-DD --saida <pasta>`. Ele acha as capas do dia de sete jornais no
  vercapas.com.br e baixa cada uma para `<pasta>/<slug>.jpg`.
- Abra cada imagem (ferramenta Read) e transcreva só a manchete principal, exatamente como impressa, em caixa normal.
  Nada além da manchete: o texto das capas não é reproduzido.
- Grave no boletim da manhã o campo `"capas": [{"jornal", "manchete", "imagem", "pagina", "site"}]`, com os valores de
  `capas.json` (as imagens ficam no VerCapas; não suba as capas para o site nem para o artefato).
- Jornal sem capa na data fica de fora; diga no relatório.

## 4. Publicar
Siga `tools/PUBLICAR.md` inteiro (ponte com o Radar, exportação, `montar_site.py`, commit "Boletim da manhã de DD/MM" ou "Boletim da noite de DD/MM", push).
Antes de publicar, faça as leituras limpas das fontes do boletim (`tools/LEITURAS.md`, tipo "noticia", campo `url`
igual ao do boletim): abra cada página com WebFetch ou curl simples; as que recusarem acesso vão para "pulados". Grave na coleção
`leituras` e só então exporte e publique. Se nenhum dos dois funcionar nesta execução, pule as leituras e registre.

## 5. Relatório final
Uma resposta curta: manchete, número de notas, o que foi pulado e por quê, e o hash do commit.
