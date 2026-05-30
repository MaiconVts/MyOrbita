# Planejamento — Refatoração da Documentação MyOrbita

## Estrutura Final Definida

| # | Arquivo | Conteúdo |
|---|---|---|
| 1 | `docs/01_CONTEXTO_PROJETO.md` | Estado atual por camada, sprints, dependências — base para todos os outros |
| 2 | `docs/02_ARQUITETURA.md` | Padrões de projeto, fluxo de dados, decisões de design |
| 3 | `docs/03_DADOS.md` | IVaga, normalização, mapeamentos, dedup, ID determinístico |
| 4 | `docs/04_CI_CD.md` | Workflows, crons, timeouts, checkpoint, enriquecedor |
| 5 | `docs/05_ANTI_DETECCAO.md` | 12 camadas LinkedIn, filtros validados, lições aprendidas |
| 6 | `docs/06_PLANO_TESTES.md` | Plano de testes (revisão menor) |
| 7 | `docs/07_CLAUDE.md` | Contexto IA, perfil, convenções, roadmap atualizado |
| 8 | `README.md` | Visão geral, stack resumido, link do projeto, como rodar |

---

## Ordem de Execução

1. `01_CONTEXTO_PROJETO.md` — primeiro por ser base dos demais
2. `02_ARQUITETURA.md`
3. `03_DADOS.md`
4. `04_CI_CD.md`
5. `05_ANTI_DETECCAO.md`
6. `06_PLANO_TESTES.md`
7. `07_CLAUDE.md`
8. `README.md` — por último (ou deixar para outra sessão)

---

## Problemas Identificados para Corrigir em Cada Doc

### Geral (todos os docs)
- [ ] Remover variáveis de ambiente hardcoded (URLs do Firebase, API keys, IDs)
- [ ] Remover referências a `geoId=106057199` como requisito — não é necessário e filtrar vagas do exterior não é problema
- [ ] Eliminar repetições entre documentos (cache citado em 3 lugares diferentes)
- [ ] Atualizar estrutura de arquivos — incluir `linkedin_enricher.py`, `main_linkedin_enricher.py`, `linkedin_enricher.yml`
- [ ] Atualizar workflows — eram 2 (`gupy.yml` + `linkedin.yml`), agora são 4 (`gupy.yml`, `linkedin-dev.yml`, `linkedin-adv.yml`, `linkedin_enricher.yml`)

### `CONTEXTO_PROJETO.md`
- [ ] Atualizar seção 2.1 Backend — tabela de arquivos está desatualizada (falta enricher)
- [ ] Atualizar crons e horários dos workflows

### `CLAUDE.md`
- [ ] Roadmap: projeto está quase finalizado, ajustar status das sprints
- [ ] Remover `geoId` da seção de filtros validados
- [ ] Atualizar anti-detecção de 11 para 12 camadas
- [ ] Remover variáveis de ambiente com valores reais

### `PLANO_TESTES.md`
- [ ] Revisão menor — verificar se estrutura de diretórios bate com o atual

### Cache
- [ ] Verificar implementação prática do cache (`useCacheVagas`) — está citado em 3 pontos diferentes, possível inconsistência
- [ ] Confirmar se está funcionando corretamente antes de documentar

---

## Prompt para Nova Sessão

```
Contexto: estou refatorando a documentação do MyOrbita seguindo o planejamento em PLANEJAMENTO_DOCS.md.

Estrutura definida: 8 arquivos numerados em docs/ + README.md na raiz.
Ordem de execução: começar por 01_CONTEXTO_PROJETO.md.

Problemas a corrigir:
- Remover variáveis de ambiente/URLs hardcoded
- Remover geoId como requisito
- Eliminar repetições (cache em 3 lugares)
- Atualizar lista de arquivos (incluir linkedin_enricher.py, main_linkedin_enricher.md, linkedin_enricher.yml)
- Atualizar workflows de 2 para 4
- Roadmap atualizado (projeto quase finalizado)
- Verificar cache na prática antes de documentar

Arquivos atuais na pasta docs/:
- CLAUDE.md
- CONTEXTO_PROJETO.md  
- PLANO_TESTES.md

README.md está na raiz.

Me peça os arquivos um por um conforme precisar.
```

Ser transparente quanto ao uso de i.a. para resolve problemas tecnicos e complexos, principalemente na medida que o
projeto escalou e ficou mais complexo hoje o projeto conta com mais de 15 mil linhas de código para manter e continuar
esse projeto com uma pessoa só seria inviável, ou demoraria anos sobre risco de demorar muito para ser concluido, a i.a.
Claude foi vital para decisões de arquitetura, automações de actions, e facilitação na implementação de features e
design no front end, porém, 95% das decisões técnicas, arquitetura, e implementação foram feitas por mim, a i.a. 
foi uma ferramenta de apoio para acelerar o processo, mas o projeto é 100% meu, e a i.a. é apenas uma ferramenta que me
ajudou a ser mais eficiente, mas não substituiu minha visão, decisões, ou implementação e principalemente, me ajudou a
concretizar o que eu queria que fosse desde o inicio, que era o agregador de vagas, que reunia multiplas plataformas em
um lugar só, com opções de filtro. O projeto durou cerca de 4 meses, onde houve momentos de maior e menor intensidade,
de acordo com a rotina externa, porém, felizmente, consegui concluir e implementar tudo que pretendia para a primeira
versão, e deixei o caminho pronto com poo, solid, clean architecture, facilitando implementar qualquer scraper a mais,
fazendo pequenos ajustes no front e backend.