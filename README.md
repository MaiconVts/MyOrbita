<div align="center">

<a href="https://my-orbita.vercel.app/">
  <img src="./docs/assets/banner.svg" alt="MyOrbita: o nome com um anel orbital ao redor do O, sobre nebulosas, planetas em órbita, buraco negro, cometas e salto de dobra espacial animados" width="100%">
</a>

<h3>Agregador de vagas que reúne Gupy e LinkedIn em um único lugar</h3>

<p>Filtros por modalidade, estado, nível, contrato e origem, com coleta automática todos os dias.</p>

<p>
  <a href="https://my-orbita.vercel.app/"><img src="https://img.shields.io/badge/Acessar_o_MyOrbita-my--orbita.vercel.app-0b0718?style=for-the-badge&logo=vercel&logoColor=white" alt="Acessar o MyOrbita"></a>
</p>

<p>
  <a href="https://github.com/MaiconVts/MyOrbita/actions/workflows/gupy.yml"><img src="https://img.shields.io/github/actions/workflow/status/MaiconVts/MyOrbita/gupy.yml?style=flat-square&label=Scraper%20Gupy&logo=githubactions&logoColor=white" alt="Scraper Gupy"></a>
  <a href="https://github.com/MaiconVts/MyOrbita/actions/workflows/linkedin-dev.yml"><img src="https://img.shields.io/github/actions/workflow/status/MaiconVts/MyOrbita/linkedin-dev.yml?style=flat-square&label=LinkedIn%20Dev&logo=githubactions&logoColor=white" alt="Scraper LinkedIn Dev"></a>
  <a href="https://github.com/MaiconVts/MyOrbita/actions/workflows/linkedin-adv.yml"><img src="https://img.shields.io/github/actions/workflow/status/MaiconVts/MyOrbita/linkedin-adv.yml?style=flat-square&label=LinkedIn%20Jur%C3%ADdico&logo=githubactions&logoColor=white" alt="Scraper LinkedIn Jurídico"></a>
  <a href="https://github.com/MaiconVts/MyOrbita/actions/workflows/linkedin_enricher.yml"><img src="https://img.shields.io/github/actions/workflow/status/MaiconVts/MyOrbita/linkedin_enricher.yml?style=flat-square&label=Enriquecedor&logo=githubactions&logoColor=white" alt="Enriquecedor LinkedIn"></a>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11">
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black" alt="React 19">
  <img src="https://img.shields.io/badge/Vite-8-646CFF?style=flat-square&logo=vite&logoColor=white" alt="Vite 8">
  <img src="https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white" alt="Tailwind CSS 4">
  <img src="https://img.shields.io/badge/Firebase-Realtime_DB-FFCA28?style=flat-square&logo=firebase&logoColor=black" alt="Firebase Realtime Database">
  <img src="https://img.shields.io/badge/Vercel-deploy-000000?style=flat-square&logo=vercel&logoColor=white" alt="Vercel">
</p>

<p>
  <img src="https://img.shields.io/github/last-commit/MaiconVts/MyOrbita?style=flat-square&label=%C3%BAltimo%20commit" alt="Último commit">
  <img src="https://img.shields.io/github/languages/top/MaiconVts/MyOrbita?style=flat-square" alt="Linguagem principal">
  <img src="https://img.shields.io/badge/Licen%C3%A7a-Todos_os_direitos_reservados-B3261E?style=flat-square" alt="Licença: todos os direitos reservados">
</p>

<sub>Projeto solo de portfólio técnico · <a href="#o-que-é">O que é</a> · <a href="#arquitetura">Arquitetura</a> · <a href="#agenda-de-coleta">Agenda</a> · <a href="#como-rodar-localmente">Rodar localmente</a> · <a href="#documentação">Docs</a></sub>

</div>

---

## O que é

MyOrbita resolve um problema simples: buscar vagas exige acessar múltiplas plataformas manualmente, cada uma com sua própria interface e limitações. O sistema coleta vagas automaticamente todos os dias, padroniza os dados e os serve em uma interface unificada com filtros que as próprias plataformas não oferecem de forma consolidada.

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>💻 Tecnologia</h3>
      Vagas de desenvolvimento do <b>Gupy</b> e do <b>LinkedIn</b>, em <a href="https://my-orbita.vercel.app/vagas-dev"><code>/vagas-dev</code></a>.
    </td>
    <td width="50%" valign="top">
      <h3>⚖️ Direito</h3>
      Vagas jurídicas do <b>Gupy</b> e do <b>LinkedIn</b>, em <a href="https://my-orbita.vercel.app/vagas-adv"><code>/vagas-adv</code></a>.
    </td>
  </tr>
</table>

| | Recurso |
|:---:|---|
| 🔎 | Busca por título, empresa ou localização |
| 🧭 | Filtros por modalidade, nível, estado, tipo de contrato, PCD e plataforma de origem |
| ♻️ | Deduplicação por ID determinístico gerado a partir da URL |
| ⚡ | Cache local de 1h no navegador; filtros aplicados sem novas chamadas ao banco |

---

## Stack

| Camada | Tecnologia |
|---|---|
| Coleta | ![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=flat-square&logo=python&logoColor=white) `curl_cffi` · `lxml` · `requests` |
| Banco de dados | ![Firebase](https://img.shields.io/badge/Firebase_Realtime_DB-FFCA28?style=flat-square&logo=firebase&logoColor=black) |
| Automação | ![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white) |
| Frontend | ![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black) ![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black) ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white) |
| Deploy | ![Vercel](https://img.shields.io/badge/Vercel-000000?style=flat-square&logo=vercel&logoColor=white) |

---

## Arquitetura

O sistema roda inteiramente em background via GitHub Actions. Quatro workflows independentes executam diariamente em horários escalonados — scrapers de listagem, enriquecedor de dados e persistência no Firebase. O frontend consome os dados via SDK do Firebase com cache local de 1h.

```mermaid
flowchart LR
    subgraph fontes["Fontes"]
        G["Gupy<br/><sub>API REST</sub>"]
        L["LinkedIn<br/><sub>HTML</sub>"]
    end

    subgraph actions["GitHub Actions · diário"]
        SG["Scraper Gupy"]
        SL["Scrapers LinkedIn<br/><sub>Dev · Jurídico</sub>"]
        EN["Enriquecedor"]
    end

    DB[("Firebase<br/>Realtime Database")]

    subgraph web["Vercel"]
        APP["App React<br/><sub>cache local 1h</sub>"]
    end

    G --> SG
    L --> SL
    SG -->|"vagas padronizadas"| DB
    SL -->|"vagas padronizadas"| DB
    DB <-->|"detalhes da vaga"| EN
    DB -->|"SDK Firebase"| APP
```

Construído com Clean Architecture, SOLID e Design Patterns. A estrutura permite adicionar novas fontes de vagas com alterações mínimas — um novo scraper, um novo entry point, um novo workflow.

O scraper do LinkedIn usa técnicas de anti-detecção (TLS fingerprinting, delays gaussianos, circuit breaker), descritas em [`docs/05_ANTI_DETECCAO.md`](./docs/05_ANTI_DETECCAO.md).

### Agenda de coleta

| Workflow | Horário (BRT) | Cron (UTC) |
|---|:---:|:---:|
| Scraper Gupy | **03h42** | `42 6 * * *` |
| Scraper LinkedIn Dev | **04h45** | `45 7 * * *` |
| Scraper LinkedIn Jurídico | **12h00** | `0 15 * * *` |
| Enriquecedor LinkedIn | **16h00** | `0 19 * * *` |

---

## Como rodar localmente

**Pré-requisitos:** ![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white) ![Node.js](https://img.shields.io/badge/Node.js-18+-5FA04E?style=flat-square&logo=nodedotjs&logoColor=white)

```bash
# Backend
pip install -r requirements.txt
# Configurar secrets/firebase_key.json e .env
python main_gupy.py
python main_linkedin_dev.py

# Frontend
cd myorbita-web
npm install
npm run dev
```

Instruções completas de configuração em [`docs/04_CI_CD.md`](./docs/04_CI_CD.md).

---

## Documentação

Documentação técnica completa em [`/docs`](./docs).

<details>
<summary><b>Ver índice dos documentos</b></summary>
<br>

| Documento | Assunto |
|---|---|
| [`01_CONTEXTO_PROJETO.md`](./docs/01_CONTEXTO_PROJETO.md) | Contexto e objetivos do projeto |
| [`02_ARQUITETURA.md`](./docs/02_ARQUITETURA.md) | Arquitetura e organização do código |
| [`03_DADOS.md`](./docs/03_DADOS.md) | Modelo de dados |
| [`04_CI_CD.md`](./docs/04_CI_CD.md) | CI/CD e configuração do ambiente |
| [`05_ANTI_DETECCAO.md`](./docs/05_ANTI_DETECCAO.md) | Estratégias de anti-detecção |
| [`06_PLANO_TESTES.md`](./docs/06_PLANO_TESTES.md) | Plano de testes |
| [`07_CLAUDE.md`](./docs/07_CLAUDE.md) | Instruções para desenvolvimento assistido por IA |

</details>

---

## Sobre o uso de Inteligência Artificial

Este projeto foi desenvolvido com o auxílio do Claude (Anthropic) como ferramenta de desenvolvimento — e isso foi uma decisão deliberada, não uma limitação.

Com mais de 15 mil linhas de código, quatro scrapers, um sistema de enriquecimento assíncrono, pipeline de CI/CD completo e interface web com filtros avançados, manter tudo isso sozinho em cerca de quatro meses seria inviável sem o uso inteligente de ferramentas. A IA foi parte da estratégia desde o início.

> **O que a IA fez:** acelerou decisões de arquitetura, ajudou a implementar features complexas, depurou problemas difíceis de rastrear e colaborou na escrita de automações de CI/CD.

> **O que eu fiz:** cada decisão técnica e arquitetural foi tomada por mim. Defini o escopo, escolhi o stack, estruturei a arquitetura, validei cada solução proposta, identifiquei os problemas, dirigi o desenvolvimento e mantive a visão do produto do início ao fim. A IA não tomou uma decisão sequer sem que eu entendesse o que estava sendo feito e por quê.

Saber usar IA para desenvolver é uma habilidade real. Não se trata de delegar — trata-se de saber o que pedir, como avaliar o que recebe, e quando discordar. Ao longo do projeto, discordei, corrigi e refiz diversas vezes. O projeto é meu. A IA foi uma ferramenta, como um compilador ou um linter.

O resultado foi um projeto que vai além do que entregaria sozinho no mesmo tempo — e isso é exatamente o ponto.

---

## Licença

© 2026 Maicon Vitor. Todos os direitos reservados. Uso comercial proibido sem autorização expressa do autor.

<div align="center">
<br>
<a href="https://my-orbita.vercel.app/"><img src="https://img.shields.io/badge/Feito_por-Maicon_Vitor-0b0718?style=for-the-badge" alt="Feito por Maicon Vitor"></a>
<a href="https://github.com/MaiconVts"><img src="https://img.shields.io/badge/GitHub-MaiconVts-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub MaiconVts"></a>
</div>
