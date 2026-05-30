# 04 — CI/CD

> Última atualização: Maio/2026

---

## Visão Geral

A automação é feita inteiramente via GitHub Actions. Quatro workflows rodam diariamente em horários escalonados, garantindo que cada job tenha tempo suficiente para terminar antes do próximo começar.

---

## Workflows

| Workflow | Horário (BRT) | Duração média | Função |
|---|---|---|---|
| `gupy.yml` | 07:34 | ~33 min | Coleta Gupy DEV + ADV |
| `linkedin-dev.yml` | 07:59 | ~3h22 | Coleta LinkedIn DEV |
| `linkedin-adv.yml` | 12:00 | ~3h32 | Coleta LinkedIn ADV |
| `linkedin_enricher.yml` | 16:00 | ~30 min | Enriquece tipo_contrato |

O LinkedIn DEV e ADV rodam em workflows separados por causa do hard limit de 6h do GitHub Actions — os dois juntos ultrapassariam esse limite. O enriquecedor roda após todos os scrapers terminarem, garantindo que as vagas já estejam no Firebase antes do enriquecimento.

Todos os workflows suportam execução manual via `workflow_dispatch`.

---

## Credenciais

As credenciais do Firebase são injetadas via GitHub Secrets — nunca estão no repositório:

| Secret | Conteúdo |
|---|---|
| `FIREBASE_CREDENTIALS` | JSON completo da Service Account |
| `FIREBASE_DB_URL` | URL do Realtime Database |

Em cada workflow, o JSON da Service Account é escrito em `secrets/firebase_key.json` antes da execução e descartado ao final.

---

## Logs e Artefatos

Cada execução gera um `scraper.log` com progresso em tempo real, métricas finais e erros. O arquivo é enviado como artefato do workflow e fica disponível por 14 dias para diagnóstico.

Métricas registradas ao final de cada execução:
- Total de combinações pesquisadas
- Vagas únicas coletadas
- Duplicatas ignoradas
- Vagas já existentes no Firebase
- Duração total
- Taxa de erro (LinkedIn)

---

## Checkpoint e Persistência

O `scraper_runner` faz `ref.set()` no Firebase após cada combinação `keyword × modalidade` que retorna vagas novas. Isso garante que um timeout ou crash no meio da execução não perde o progresso já coletado.

O `ref.set()` substitui todos os dados da rota pelo snapshot acumulado até aquele momento. Vagas expiradas saem naturalmente a cada execução completa — não é necessário limpeza manual.

**Atenção:** executar os scrapers localmente e interromper no meio sobrescreve os dados da rota com um snapshot parcial. A próxima execução agendada restaura o conjunto completo.

---

## Instalação Local

```bash
# Dependências backend
pip install -r requirements.txt

# Configurar credenciais
mkdir secrets/
# Salvar Service Account em secrets/firebase_key.json

# Criar .env na raiz
FIREBASE_KEY_PATH=secrets/firebase_key.json
FIREBASE_DB_URL=<url-do-banco>
```

## Execução Manual

```bash
python main_gupy.py
python main_linkedin_dev.py
python main_linkedin_adv.py
python main_linkedin_enricher.py
```
