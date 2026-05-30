# 06 — Plano de Testes

> Última atualização: Maio/2026  
> Status: 📋 Pendente — Sprint 7.5

---

## Stack

| Ferramenta | Escopo |
|---|---|
| pytest | Backend — unitários, integração, resiliência |
| vitest | Frontend — unitários |
| Playwright | Frontend — E2E, responsividade, segurança, performance |
| axe-core | Acessibilidade (WCAG) via Playwright |
| Lighthouse CI (`@lhci/cli`) | Performance, SEO, boas práticas, acessibilidade (notas 0-100) |

---

## Backend

### Unitários

| Módulo | O que testar |
|---|---|
| `_normalizar_campo` | None, string vazia, espaços, bool, int, default customizado |
| `_normalizar_estado` | Nome completo → sigla, sigla já passada, desconhecido, None |
| `gerar_id_deterministico` | Mesmo link → mesmo ID, IDs diferentes, 16 chars, hexadecimal |
| `filtrar_duplicadas` | Vagas únicas, duplicatas intra-scraping, já no Firebase, lista vazia |
| `padronizar_vaga` | Todas as chaves presentes, campos opcionais com None |
| Mapeamentos Gupy | Todos os códigos de tipo_contrato e modalidade |
| Mapeamentos LinkedIn | Todos os valores de TIPO_CONTRATO_MAP |

### Integração

| Caso | O que valida |
|---|---|
| API Gupy responde 200 | Disponibilidade |
| Resposta contém `data` e `pagination` | Estrutura do JSON |
| Campos obrigatórios presentes na vaga | `name`, `jobUrl`, `workplaceType`, `type` |
| Firebase leitura/escrita | Ambiente de teste isolado |

### Resiliência

| Caso | O que simula |
|---|---|
| HTTP 429 → retry com backoff | Rate limit |
| HTTP 403/404 → abort imediato | Sem retry desnecessário |
| API retorna HTML em vez de JSON | Resposta inválida |
| API retorna JSON sem chave `data` | Estrutura inesperada |
| Request travado além do timeout | Timeout funciona |

---

## Frontend — Unitários

### `useFiltrosVagas`

- Sem filtros retorna todas as vagas
- Busca por título, empresa, cidade, estado, contrato
- Busca ignora acentos e maiúsculas
- Busca multi-termo (AND)
- Filtro de modalidade, estado, contrato, nível, PCD, origem
- Filtros combinados (AND entre filtros, OR dentro do mesmo)
- Permissividade em campos ausentes
- Ordenação recente/antiga
- Paginação (9/página, reset ao filtrar)
- `estadosDisponiveis` e `contratosDisponiveis` ignoram "Não informado"

### Utilitários

- `normalizarTexto` — acentos, lowercase, trim
- `formatarData` — ISO → dd/mm/aaaa, vazio → "—"
- `corPrazo` — verde/amarelo/vermelho conforme proximidade
- `campoValido` — null, "Não informado", valor real

---

## Frontend — E2E (Playwright)

### Responsividade
6 viewports: iPhone SE (320px), iPhone 14 (390px), iPad Mini (768px), iPad Pro (1024px), Laptop (1366px), Full HD (1920px).

- Sem scroll horizontal em nenhum viewport
- Grid de cards adapta colunas (3 → 2 → 1)
- Grid de filtros adapta colunas (4 → 2 → 1)
- Menu hamburger aparece em mobile
- Modal de vaga cabe na tela

### Segurança
- `.env` não servido pelo Vite
- `secrets/` não acessível via URL
- Inputs sanitizam XSS
- Links externos com `rel="noopener noreferrer"`
- Firebase Rules restringem escrita pública

### Usabilidade
- Card abre modal ao clicar
- Modal fecha ao clicar fora e no botão X
- Busca filtra em tempo real
- Paginação navega corretamente
- Estado vazio exibe mensagem
- Chips de filtros ativos removem filtro ao clicar

### Acessibilidade (axe-core)
- Zero violações WCAG nível A
- Contraste mínimo 4.5:1
- Navegação por teclado funcional
- Modal faz trap de foco

### Performance
- First Contentful Paint < 2s
- Largest Contentful Paint < 3s
- Filtros respondem em < 100ms
- Build size < 500KB gzip

### Lighthouse
Auditoria automatizada com notas de 0 a 100 em quatro categorias:

| Categoria | Meta |
|---|---|
| Performance | ≥ 90 |
| Acessibilidade | ≥ 90 |
| Boas Práticas | ≥ 90 |
| SEO | ≥ 90 |

Roda via `@lhci/cli` integrado ao pipeline. Falha o build se alguma categoria cair abaixo da meta definida.

### Cross-browser
Chromium, Firefox e WebKit (Safari) — página carrega sem erros, filtros funcionam, backdrop-filter renderiza.

---

## CI — Integração ao GitHub Actions

Todos os testes rodam automaticamente a cada push. Logs e relatórios disponíveis como artefato no Actions por 14 dias.

```yaml
- name: Testes backend (unitários + integração + resiliência)
  run: pytest tests/ -v --cov=scrapers --cov-report=html

- name: Testes frontend unitários
  run: |
    cd myorbita-web
    npm ci
    npx vitest run

- name: Testes E2E (responsividade + segurança + usabilidade + acessibilidade + performance + cross-browser)
  run: |
    cd myorbita-web
    npx playwright install --with-deps
    npx playwright test

- name: Lighthouse CI
  run: |
    cd myorbita-web
    npm run build
    npx lhci autorun

- name: Upload relatórios
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: |
      htmlcov/
      myorbita-web/playwright-report/
      myorbita-web/.lighthouseci/
    retention-days: 14
```

---

## Cobertura Alvo

| Camada | Meta |
|---|---|
| Backend unitários | 90%+ |
| Frontend unitários | 80%+ |
| E2E responsividade | 100% dos viewports |
| E2E segurança | 100% dos checks |
| Acessibilidade WCAG A | 0 violações |
| Lighthouse todas as categorias | ≥ 90 |
