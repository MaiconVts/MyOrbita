# Pendências — myorbita-web

## Concluído (05/10/2026): redesign Carta Estelar
- Contrato da direção em `.impeccable/surfaces/myorbita-web-src-pages-home-jsx.md`.
- **Home (landing):**
  - Hero com o PlanetarySystem e a nova marca (My/Orbita em Unbounded, anel e satélite no O).
  - Painel de bordo com contagens reais, últimas vagas, como funciona e FAQ factual (horários reais de coleta).
- **ListaVagas unificada** (`/vagas-dev` e `/vagas-adv`):
  - Faixas por dia de coleta e selo "Nova" desde a última visita.
  - Filtros sincronizados na URL e ordenação nas duas áreas (com ícone).
- **Header, VagaDetalhe, modais e rodapé** reconstruídos sobre `styles/carta.css`.
- **SEO:**
  - Pré-render de `/`, `/vagas-dev` e `/vagas-adv` (`scripts/prerender.mjs`) e `cleanUrls` no `vercel.json`.
  - Meta por página, canônica, JSON-LD, Open Graph e Twitter.
  - `og-myorbita.png`, `apple-touch-icon.png` e o novo `favicon.svg`, com o gerador em `tools/banner/gen_og.py`.
  - `robots.txt` e `sitemap.xml`.
- **Performance:**
  - Rotas carregadas sob demanda e Firebase carregado só na primeira busca.
  - Bibliotecas em pedaços separados (react, motion e firebase).
  - O JS principal caiu de 714 kB para 52 kB.
- **Verificação feita:**
  - `eslint` e build limpos, `impeccable detect` sem achados.
  - Playwright em 375, 768 e 1440 px e com movimento reduzido; console sem erros.

## Concluído (05/10/2026): limpeza do front
- Link de apoio (Ko-fi) no rodapé, lido de `SITE.apoio` em `src/config/site.js`. Com o valor vazio, o link fica oculto.
- `sitemap.xml` passou a ser gerado no build por `scripts/prerender.mjs`, com as mesmas rotas do pré-render e `lastmod` do dia. O arquivo estático em `public/` foi removido.
- framer-motion com `LazyMotion` + `m`. Os recursos (`domMax`) carregam depois da primeira pintura, em `utils/recursosMotion.js`. O pedaço `motion` caiu de 259 kB para 131 kB e agora contém só GSAP e Lenis. Mais 70 kB foram adiados.
- `@rive-app/react-canvas` removido, junto com dois arquivos mortos: `constants/colors.js` e `CreditoDesenvolvedor/index.jsx`.
- `.vazio__giro` agora usa o token `--dur-giro-vazio`.

## Concluído (05/10/2026): polish
- Removidos os marcadores-sobrancelha das seções da Home ("01 · Rotas" a "04 · Perguntas" e "Próxima parada"). Os títulos das seções agora usam `text-wrap: balance`.
- ListaVagas: o subtítulo da área desceu para baixo do H1. No celular, plataforma, nível, estado, contrato e PCD ficam atrás do botão "Mais filtros", que mostra quantos estão ativos, e a primeira vaga aparece já na primeira tela.

## Em aberto: só backend e segurança
- **Ko-fi:** preencher `SITE.apoio` em `myorbita-web/src/config/site.js` com a URL da página (é a única ação do dono no front).
- **Backend Gupy:** descobrir o endpoint novo e não gravar `ref.set({})` com lista vazia (ver `STATUS.md`, itens 1 a 3).
- **Página por vaga com JobPosting:** depende do backend. Precisa de ID estável por vaga e de dados no build (ou SSR). Também é preciso confirmar se o Google aceita JobPosting de agregador com vagas do LinkedIn.
- **Recuperar o histórico apagado:** são dados do Firebase (backend).
- **Segurança:**
  - Revisar as regras do Realtime Database: leitura pública e escrita só pela conta de serviço.
  - Restringir a chave web do Firebase por domínio no Google Cloud.
  - Adicionar CSP e cabeçalhos de segurança no `vercel.json`.
- **Opcional:** rodar `impeccable-finish-reviewer` e `impeccable-documenter`, medir o fps do céu, fazer commit e deploy.
