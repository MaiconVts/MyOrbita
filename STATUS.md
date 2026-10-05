# Estado do Projeto — MyOrbita

> Documento de acompanhamento. Atualize a data, os checkboxes e o histórico no fim a cada retomada.
> **Última revisão:** 02/10/2026

---

## Resumo

| Área | Estado | Observação |
|---|---|---|
| Site em produção ([my-orbita.vercel.app](https://my-orbita.vercel.app/)) | ✅ No ar | `/`, `/vagas-dev` e `/vagas-adv` respondem 200 |
| Scraper **Gupy** (DEV + ADV) | 🔴 **Quebrado desde 01/10** | API devolve 404, as rotas no Firebase foram apagadas e o workflow continua verde |
| Scraper **LinkedIn DEV** | ✅ Estável | 50/50 execuções com sucesso, ~205 min |
| Scraper **LinkedIn ADV** | 🟠 No limite | Encosta nas 6h do GitHub Actions: 9 canceladas e 2 falhas nas últimas 50 |
| **Enriquecedor** LinkedIn | ✅ Roda | 50/50 com sucesso, ~65 min (ver hipótese de sobreposição no item 4) |
| Frontend: build | ✅ Passa | 617 KB de JS (188 KB gzip), num chunk só |
| Frontend: lint | 🟡 4 erros, 1 aviso | Regras novas do `eslint-plugin-react-hooks` 7 |
| Testes automatizados | 📋 Não iniciados | Sprint 7.5 continua só no plano ([docs/06_PLANO_TESTES.md](docs/06_PLANO_TESTES.md)) |
| Kit de design (skills, regras, MCPs) | 🆕 Instalado, ainda sem commit | Falta `PRODUCT.md`; nenhuma tela passou pelo fluxo novo ainda |

**Dados servidos hoje** (leitura pública do Firebase em 02/10):

| Rota | Vagas | `tipo_contrato` "Não informado" | `state` "Não informado" |
|---|---|---|---|
| `/vagas/dev/gupy` | **0 (rota vazia)** | — | — |
| `/vagas/adv/gupy` | **0 (rota vazia)** | — | — |
| `/vagas/dev/linkedin` | 2.097 | 68% | 23% |
| `/vagas/adv/linkedin` | 1.911 | 91% | 13% |

Antes da quebra, o Gupy entregava cerca de 1.800 vagas DEV e 1.080 ADV por dia. Hoje o site mostra só vagas do LinkedIn.

---

## 🔴 Urgente

### 1. Gupy fora do ar e rotas apagadas
- **Sintoma:** desde a execução de 01/10, todas as 1.368 buscas recebem `HTTP 404` de `https://employability-portal.gupy.io/api/v1/jobs` ([scrapers/gupy_scraper.py:117](scrapers/gupy_scraper.py#L117)). Confirmei hoje com uma requisição manual: 404 do nginx. A última execução boa foi a de 30/09.
- **Por que as rotas sumiram:** o checkpoint a cada 10 keywords ([scraper_runner.py:315-317](scraper_runner.py#L315-L317)) chama `enviar_para_firebase()` mesmo com a lista vazia, e o `ref.set({})` apaga a rota. A mensagem final "Firebase não atualizado" ([scraper_runner.py:356](scraper_runner.py#L356)) engana, porque o checkpoint já zerou tudo antes.
- **Por que ninguém percebeu:** o workflow termina com sucesso mesmo com 0 vagas coletadas.
- **A fazer:**
  - [ ] Descobrir o endpoint novo da Gupy (inspecionar a rede do portal de vagas) e atualizar o scraper
  - [ ] Nunca chamar `ref.set()` com lista vazia (checkpoint e envio final)
  - [ ] Falhar o job (exit code ≠ 0) quando a coleta ficar abaixo de um mínimo por categoria

### 2. LinkedIn ADV batendo no limite de 6h
- O ADV tem **153 keywords × 3 modalidades = 459 combinações**, contra 261 do DEV. O comentário do workflow ainda fala em "~15-20 keywords" ([.github/workflows/linkedin-adv.yml:18](.github/workflows/linkedin-adv.yml#L18)) e a doc fala em ~3h32.
- Desde o fim de julho as execuções que terminam levam de 352 a 360 min, e as que estouram são canceladas pelo GitHub. Nas últimas 50: 39 sucessos, 9 cancelamentos e 2 falhas (uma delas foi desligamento do runner).
- Muitas keywords do ADV devolvem quase só duplicatas: há logs com "120 duplicadas, 0 novas" e com dezenas de vagas rejeitadas pelo filtro de relevância (ex.: "Procurador Municipal" trazendo vagas de compras).
- **A fazer:**
  - [ ] Auditar `queries/advogados_linkedin.json`: cortar keywords redundantes ou de baixo rendimento
  - [ ] Ou dividir o ADV em dois workflows, como já foi feito entre DEV e ADV

---

## 🟠 Importante

### 3. Rotas parciais durante toda execução
A cada combinação com vaga nova, o runner faz `ref.set()` só com o que acumulou **nesta** execução ([scraper_runner.py:307](scraper_runner.py#L307)). Na primeira keyword do dia, a rota cai de cerca de 2.000 vagas para cerca de 100 e vai crescendo de novo. Na prática o site mostra dados incompletos durante ~3h30 por dia (LinkedIn DEV) e ~6h (LinkedIn ADV), atenuado só pelo cache local de 1h. Quando o ADV é cancelado, a rota fica incompleta até o dia seguinte.
- [ ] Gravar numa rota temporária e trocar no fim, ou usar `update()` durante a coleta e limpar as vagas expiradas só ao final

### 4. Hipótese: o enriquecedor perde trabalho no ADV
Os horários agendados atrasam de 4 a 7 horas no GitHub (exemplo: o cron do enriquecedor é 19:00 UTC e ele roda entre 21:40 e 23:40 UTC). Com isso, o enriquecedor roda **no meio** do LinkedIn ADV (que vai de ~19:00 a ~01:00 UTC). O ADV só preserva o `tipo_contrato` que estava no snapshot carregado no início, então os checkpoints seguintes sobrescrevem o que o enriquecedor acabou de gravar. Isso bate com os 91% de "Não informado" no ADV contra 68% no DEV, mas ainda **não confirmei pelos logs**.
- [ ] Confirmar e, se for isso, mover o enriquecedor para depois do ADV (ou encadear com `workflow_run`)

### 5. Avisos de manutenção do CI
- [ ] `actions/checkout@v4` e `actions/setup-python@v5` usam Node 20, que o GitHub está descontinuando (aviso em todos os logs). Atualizar as versões.

### 6. Lint do frontend
- [ ] [useCacheVagas.js:104-105](myorbita-web/src/hooks/useCacheVagas.js#L104-L105): lê e escreve ref durante o render (`react-hooks/refs`)
- [ ] [useFiltrosVagas.js:226](myorbita-web/src/hooks/useFiltrosVagas.js#L226): `setState` síncrono dentro de effect para resetar a página
- [ ] [PageTransition.jsx:13](myorbita-web/src/components/PageTransition.jsx#L13): dependências faltando no `useEffect` (aviso)

---

## 🟡 Higiene e dívida técnica

**Repositório**
- [ ] `.gitignore` quebrado: a linha `.claude/` perdeu a quebra de linha ao receber o bloco do kit e virou `.claude/# Editores`. Na prática `.claude/` **deixou de ser ignorado** e há 107 arquivos novos não rastreados, incluindo `impeccable.exe` com 15 MB. Precisa decidir se as skills entram no repositório público.
- [ ] `.gitignore` ainda cita `code-hive-web/.env` (resto de outro projeto) e tem seções vazias ("Dependências", "Sistema operacional")
- [ ] `package-lock.json` está no `.gitignore`, então o build da Vercel não é reproduzível
- [ ] `queries/advogados_linkedin.json` declara `plataformas_alvo: ["gupy"]` (cópia do arquivo do Gupy)

**Frontend**
- [ ] `@rive-app/react-canvas` está instalado e não é usado; os comentários de `constants/colors.js` ainda falam do Rive
- [ ] A fonte **Space Grotesk** é citada em 10 lugares mas nunca é carregada (sem `<link>` nem `@font-face`), então cai na sans-serif do sistema
- [ ] `index.html` com `lang="en"` num site em português
- [ ] `VagasDev.jsx` (777 linhas) e `VagasAdv.jsx` (876 linhas) são quase iguais: só 327 linhas de diferença
- [ ] Cerca de 250 cores hex fixas nos componentes; `COLORS` e `TYPOGRAPHY` só são usados em `PlanetarySystem.jsx`
- [ ] Nenhum tratamento de `prefers-reduced-motion`

**Documentação desatualizada**
- [ ] [docs/07_CLAUDE.md](docs/07_CLAUDE.md) e [docs/01_CONTEXTO_PROJETO.md](docs/01_CONTEXTO_PROJETO.md) ainda dizem "deploy pendente"
- [ ] [docs/04_CI_CD.md](docs/04_CI_CD.md): horários e durações não batem com os crons nem com as execuções reais
- [ ] O cabeçalho do `scraper_runner.py` fala em "checkpoint a cada 10 keywords", mas ele grava também a cada combinação com vaga nova

---

## Frontend: retrato atual

- **Stack:** React 19, Vite 8, Tailwind 4, React Router 7, Zustand, Firebase SDK 12, `framer-motion` 12, Lucide
- **Telas:** `Home`, `VagasDev`, `VagasAdv`, mais os modais (Sobre, Como usar, Como funciona, Termos, Privacidade) e `VagaDetalhe`
- **Atmosfera:** `PlanetarySystem.jsx` desenha o fundo espacial em 3 canvas (nebulosas estáticas, estrelas e planetas a ~20 fps, warp a 60 fps). `PageTransition` usa framer-motion.
- **Identidade atual:** fundo `#150F28`/`#050015`, âmbar `#FFB703` e azul `#4FC3F7`, tema espacial (órbita/sistema solar)
- **Estilo:** mistura de Tailwind, `<style>` inline em JSX e objetos `style={{}}`, sem camada de tokens de verdade

---

## Kit de design novo (ainda sem commit)

**O que entrou:**
- [CLAUDE.md](CLAUDE.md): fluxo de design (prompt → tokens → motion → verificação com Playwright em 375/768/1440 → `/impeccable critique` e `polish`)
- [DESIGN.md](DESIGN.md): semente da assinatura visual, com paleta e tipografia em aberto
- [.claude/rules/house-style.md](.claude/rules/house-style.md) e [.claude/rules/motion-guardrails.md](.claude/rules/motion-guardrails.md)
- [prompts/prototyping-prompt.md](prompts/prototyping-prompt.md): roteiro para levantar identidade antes do código
- 19 skills: impeccable, signature-effects, design-taste-frontend, high-end-visual-design, redesign-existing-projects, emil-design-eng, animate, review-animations, motion, 8× gsap-\*, web-shaders, full-output-enforcement
- 4 agentes `impeccable-*`, e `.mcp.json` com Figma, Playwright, Context7 e Chrome DevTools

**Lacunas entre o kit e o projeto:**
- Falta o `PRODUCT.md`: o `CLAUDE.md` pede `/impeccable init` antes de qualquer tela
- As bibliotecas padrão do `house-style.md` não estão instaladas: GSAP + Lenis, tsParticles, Paper Shaders, Culori. O projeto usa `framer-motion`, que é o nome antigo do pacote `motion` (o kit espera `motion/react`)
- O `CLAUDE.md` exige tudo vindo de tokens, e hoje quase nada vem
- **Conflito de papel:** o [docs/07_CLAUDE.md](docs/07_CLAUDE.md) define a IA como mentora socrática que "nunca entrega código pronto", enquanto o `CLAUDE.md` novo manda implementar. Vale decidir qual modo vale para o trabalho de design.
- O `DESIGN.md` diz "3D só com objeto real". Os planetas do canvas são 2D e combinam com a assinatura (desenhos de fundo, linhas de órbita), então dá para manter.

**Sugestão de roteiro para testar as skills:**
1. `/impeccable init`, usando o `prompts/prototyping-prompt.md` como base, para gerar o `PRODUCT.md`
2. `/impeccable critique` na Home atual, como linha de base antes de mudar algo
3. Extrair tokens (cores, tipografia, raios, durações, easings) e carregar a Space Grotesk ou trocar a fonte
4. Redesenhar a **Home** primeiro: é a tela de "marketing", onde vale a intensidade de motion 8
5. Depois `VagasDev`/`VagasAdv`, que são telas de operação: a assinatura fica no cabeçalho, nos estados vazios e nas transições. Bom momento para unificar as duas páginas num componente só.

---

## Próximos passos, por prioridade

1. [ ] Consertar o Gupy (endpoint novo, nunca gravar lista vazia, falhar o job sem coleta)
2. [ ] Resolver o tempo do LinkedIn ADV (cortar keywords ou dividir o workflow)
3. [ ] Corrigir o `.gitignore` e decidir o que do kit de design vai para o Git
4. [ ] Confirmar a hipótese do enriquecedor e reordenar os horários
5. [ ] Escrita atômica no Firebase (sem rota parcial durante a execução)
6. [ ] Zerar o lint e atualizar as actions
7. [ ] Começar o fluxo de design (`/impeccable init` → critique → tokens → Home)
8. [ ] Sprint 7.5: testes, começando pelos unitários de `scraper_runner` (o bug do item 1 seria pego por um teste de checkpoint)
9. [ ] Atualizar a documentação em `docs/`

---

## Histórico do acompanhamento

| Data | O que mudou |
|---|---|
| 02/10/2026 | Primeira revisão após a pausa de 01/06 a 02/10 (hoje só entrou o commit do crédito no rodapé). Achados: Gupy quebrado desde 01/10 com rotas apagadas, ADV no limite de 6h, kit de design instalado e ainda sem commit. |
