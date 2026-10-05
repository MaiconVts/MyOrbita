---
version: 1
slug: "myorbita-web-src-pages-home-jsx"
primary_target: "myorbita-web/src/pages/Home.jsx"
related_targets: ["myorbita-web/src/pages/VagasDev.jsx","myorbita-web/src/pages/VagasAdv.jsx"]
---

## Scope

Home (`/`) em modo Persuade; listas `/vagas-dev` e `/vagas-adv` em modo Operate, unificadas num componente parametrizado pela área. Mesmo mundo nas três rotas.

Público: candidatos de tech e jurídico. Tarefa: ver as vagas novas da área, filtrar, sair para a candidatura na origem. Prova: contagens reais do Firebase, data da última coleta. Restrições: cores, efeitos e sistema planetário fixos (PRODUCT.md); SEO com pré-render de `/`, `/vagas-dev`, `/vagas-adv`.

## Direction contract

THESIS: o mercado de vagas como uma carta estelar de navegação: os filtros traçam o rumo e cada vaga é um porto marcado. Recusa o padrão de site de vagas (busca + cards iguais em grade) e o clichê espacial de painéis neon.

OWN-WORLD: velino noturno (roxo-tinta #150F28 com manchas de maré = nebulosas), linhas de costa e constelações em azul #4FC3F7 com traço fino, rota ativa em âmbar #FFB703. Duas luzes só na interface; estrelas coloridas ficam no canvas. Letras gravadas de carta antiga nos títulos, rótulos ao longo de linhas de rumo, numerais de coordenada em mono, anotações de margem em itálico. Vidro = placas de vidro sobre o céu vivo. Rosa dos ventos como peça de identidade.

STORY: o visitante entende em uma linha que o MyOrbita junta vagas remotas de tech e direito do Gupy e LinkedIn todo dia; acredita porque vê as contagens de hoje e a hora da coleta; escolhe um rumo e chega a uma vaga e à candidatura na origem.

FIRST VIEWPORT: eixo simétrico. No centro, a rosa dos ventos com o sistema planetário dentro (ocular). Acima, o título MyOrbita em capitais gravadas e a linha de oferta. Dois rumos saem da rosa: à esquerda Tech (azul), à direita Jurídico (âmbar), cada um com a contagem de hoje em numeral grande e o botão de ação "Ver vagas". Anotação de margem: última coleta e fontes. No celular: título, rosa menor, rumos empilhados.

FORM: Carta Estelar de Navegação (salt-stiffened treasure map, wayfinding-cartography-signage-salt-stiffened-treasure-map), fundida com o produto; rodada ousada 1, carta líder do baralho; seed key ba35a0a4. Raises: ordem de transmissão (só vagas novas recebem moldura âmbar), tiras de teste (lista em faixas por dia de coleta), filtros como camadas (colar/retirar, contagem reage ao vivo), eixo e sequência (contagens acordam em ordem ao rolar).
Signature interaction: a rota âmbar se desenha (stroke-dashoffset) da rosa até o rumo sob hover/foco e ao entrar; na lista, aplicar filtros retraça a rota e o contador da leitura corre até o novo total. Motion grammar: traço que se desenha, nada de saltos; tokens únicos de duração/curva; reduced-motion = fades curtos.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Unresolved

- Link do PayPal para o botão "me pague um café" (não inventar).
- Página por vaga com JobPosting fica para a segunda etapa.
