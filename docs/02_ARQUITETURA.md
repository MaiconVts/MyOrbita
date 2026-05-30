# 02 — Arquitetura

> Última atualização: Maio/2026

---

## Visão Geral

O sistema é composto por três camadas desacopladas: coleta (scrapers Python), persistência (Firebase Realtime DB) e apresentação (React). Cada camada evolui independentemente sem impactar as outras.

```
GitHub Actions (workflows independentes)
        │
        ├──► gupy.yml              ──► main_gupy.py              ──► GupyScraper
        ├──► linkedin-dev.yml      ──► main_linkedin_dev.py      ──► LinkedinScraper
        ├──► linkedin-adv.yml      ──► main_linkedin_adv.py      ──► LinkedinScraper
        └──► linkedin_enricher.yml ──► main_linkedin_enricher.py ──► LinkedinEnricher
                                                │
                                      scraper_runner.py
                                      (orquestração compartilhada)
                                                │
                                                ▼
                                      Firebase Realtime DB
                                      /vagas/dev/{gupy,linkedin}
                                      /vagas/adv/{gupy,linkedin}
                                                │
                                                ▼
                                          Web App (React)
                                          Mobile App (planejado)
```

---

## Padrões de Projeto

### Template Method — `BaseScraper`
`BaseScraper` é uma classe abstrata que define o contrato obrigatório para qualquer scraper. O método `buscar_vagas()` é abstrato — cada scraper implementa sua própria estratégia de coleta. O método `padronizar_vaga()` é concreto e garante que toda vaga saia com as mesmas chaves padronizadas, independente da fonte.

Adicionar um novo scraper significa criar uma subclasse de `BaseScraper` e implementar `buscar_vagas()` — nada mais precisa ser alterado.

### Strategy Pattern — Entry Points Isolados
Cada `main_*.py` instancia seu scraper específico e delega ao `scraper_runner`. Respeita o Princípio Aberto/Fechado: novas fontes entram com um novo `main_*.py` e um novo workflow, sem tocar no código existente.

### DRY via Composição — `scraper_runner.py`
Toda lógica compartilhada (logging, Firebase, deduplicação, checkpoints, métricas) vive em um único módulo. Os entry points ficam com ~20 linhas cada, concentrando apenas o que é específico da plataforma.

### Protocol Typing
O `scraper_runner` aceita qualquer objeto que satisfaça `ScraperProtocol` — não exige herança. Duck typing formal do Python 3.8+.

---

## Backend

### Orquestração
O `scraper_runner` é o núcleo do backend. Ele carrega as queries do JSON, pré-carrega os IDs existentes no Firebase para deduplicação, executa o loop de buscas e faz checkpoints incrementais. Cada checkpoint usa `ref.set()` com o snapshot completo acumulado até aquele momento — vagas expiradas saem naturalmente a cada execução completa.

### Enriquecedor Assíncrono
O `LinkedinEnricher` herda `LinkedinScraper` e reutiliza toda a camada de request (session, warm-up, delays, circuit breaker). Roda como job separado após todos os scrapers, evitando que o scraper de listagem faça requests extras por vaga — o que multiplicava o volume de requests em 60x e gerava detecção.

**Fluxo:**
1. Lê vagas com `tipo_contrato == "Não informado"` do Firebase
2. Acessa a página interna de cada vaga
3. Extrai `tipo_contrato` do JSON-LD (`employmentType`) ou HTML
4. Atualiza apenas o campo alterado via `ref.child(id).update()`

### Deduplicação em 3 Níveis
A mesma vaga pode ser retornada por múltiplas keywords. A deduplicação opera em três camadas, todas O(1) via hash:

| Nível | Mecanismo | Escopo |
|---|---|---|
| 1 | `set` de URLs vistas na execução | Intra-scraping |
| 2 | `set` de IDs carregados do Firebase | Cross-execução |
| 3 | ID MD5 determinístico por URL | Idempotência |

---

## Frontend

### Separação de Responsabilidades

| Camada | Responsabilidade |
|---|---|
| `services/api.js` | Fetch do Firebase com Promise.allSettled |
| `hooks/useCacheVagas.js` | Cache localStorage TTL 1h, isolado por rota |
| `hooks/useFiltrosVagas.js` | Pipeline de 8 filtros + paginação |
| `pages/VagasDev`, `VagasAdv` | Renderização e interação |

### Pipeline de Filtros
Aplicados em sequência via `useMemo`. Recomputado apenas quando algum filtro ou a lista de vagas muda:

```
busca textual → modalidade → nível → estado → contrato → PCD → origem → ordenação → paginação
```

Lógica: **OR dentro do mesmo filtro, AND entre filtros diferentes.**

Campos ausentes recebem tratamento permissivo — a vaga passa em qualquer seleção daquele filtro específico, mas continua sujeita aos demais. Evita que dados incompletos do scraper eliminem vagas potencialmente relevantes.

---

## Estrutura de Arquivos

```
MyOrbita-Scraper/
├── .github/workflows/
│   ├── gupy.yml
│   ├── linkedin-dev.yml
│   ├── linkedin-adv.yml
│   └── linkedin_enricher.yml
├── docs/
├── myorbita-web/
│   └── src/
│       ├── components/
│       ├── constants/
│       ├── hooks/
│       ├── pages/
│       ├── services/
│       ├── stores/
│       └── types/
├── queries/
│   ├── tecnologia_gupy.json
│   ├── tecnologia_linkedin.json
│   ├── advogados_gupy.json
│   └── advogados_linkedin.json
├── scrapers/
│   ├── base_scraper.py
│   ├── gupy_scraper.py
│   ├── linkedin_scraper.py
│   └── linkedin_enricher.py
├── main_gupy.py
├── main_linkedin_dev.py
├── main_linkedin_adv.py
├── main_linkedin_enricher.py
└── scraper_runner.py
```
