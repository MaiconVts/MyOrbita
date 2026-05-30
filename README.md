# MyOrbita

Agregador de vagas profissionais que reúne oportunidades do Gupy e LinkedIn em um único lugar, com filtros avançados por modalidade, estado, nível, contrato e origem.

> Projeto solo de portfólio técnico. Todos os direitos reservados.

![Scraper Gupy](https://github.com/MaiconVts/MyOrbita/actions/workflows/gupy.yml/badge.svg)
![Scraper LinkedIn DEV](https://github.com/MaiconVts/MyOrbita/actions/workflows/linkedin-dev.yml/badge.svg)
![Scraper LinkedIn ADV](https://github.com/MaiconVts/MyOrbita/actions/workflows/linkedin-adv.yml/badge.svg)
![Enriquecedor LinkedIn](https://github.com/MaiconVts/MyOrbita/actions/workflows/linkedin_enricher.yml/badge.svg)

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?logo=tailwindcss&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-Realtime_DB-FFCA28?logo=firebase&logoColor=black)
![License](https://img.shields.io/badge/Licença-All_Rights_Reserved-red)

**[🔗 Acessar o projeto]** ← link após deploy

---

## O que é

MyOrbita resolve um problema simples: buscar vagas exige acessar múltiplas plataformas manualmente, cada uma com sua própria interface e limitações. O sistema coleta vagas automaticamente todos os dias, padroniza os dados e os serve em uma interface unificada com filtros que as próprias plataformas não oferecem de forma consolidada.

Duas categorias disponíveis: **Tecnologia** e **Direito**, cada uma com vagas do Gupy e LinkedIn.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Coleta | Python 3.11 + `curl_cffi` + `lxml` + `requests` |
| Banco de dados | Firebase Realtime Database |
| Automação | GitHub Actions |
| Frontend | React + Vite + JavaScript + Tailwind CSS |
| Deploy | Vercel |

---

## Arquitetura

O sistema roda inteiramente em background via GitHub Actions. Quatro workflows independentes executam diariamente em horários escalonados — scrapers de listagem, enriquecedor de dados e persistência no Firebase. O frontend consome os dados via SDK do Firebase com cache local de 1h.

Construído com Clean Architecture, SOLID e Design Patterns. A estrutura permite adicionar novas fontes de vagas com alterações mínimas — um novo scraper, um novo entry point, um novo workflow.

Documentação técnica completa em [`/docs`](./docs).

---

## Como rodar localmente

**Pré-requisitos:** Python 3.11+, Node.js 18+

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

## Sobre o uso de Inteligência Artificial

Este projeto foi desenvolvido com o auxílio do Claude (Anthropic) como ferramenta de desenvolvimento — e isso foi uma decisão deliberada, não uma limitação.

Com mais de 15 mil linhas de código, quatro scrapers, um sistema de enriquecimento assíncrono, pipeline de CI/CD completo e interface web com filtros avançados, manter tudo isso sozinho em cerca de quatro meses seria inviável sem o uso inteligente de ferramentas. A IA foi parte da estratégia desde o início.

**O que a IA fez:** acelerou decisões de arquitetura, ajudou a implementar features complexas, depurou problemas difíceis de rastrear e colaborou na escrita de automações de CI/CD.

**O que eu fiz:** cada decisão técnica e arquitetural foi tomada por mim. Defini o escopo, escolhi o stack, estruturei a arquitetura, validei cada solução proposta, identifiquei os problemas, dirigi o desenvolvimento e mantive a visão do produto do início ao fim. A IA não tomou uma decisão sequer sem que eu entendesse o que estava sendo feito e por quê.

Saber usar IA para desenvolver é uma habilidade real. Não se trata de delegar — trata-se de saber o que pedir, como avaliar o que recebe, e quando discordar. Ao longo do projeto, discordei, corrigi e refiz diversas vezes. O projeto é meu. A IA foi uma ferramenta, como um compilador ou um linter.

O resultado foi um projeto que vai além do que entregaria sozinho no mesmo tempo — e isso é exatamente o ponto.

---

## Licença

© 2026 Maicon Vitor. Todos os direitos reservados. Uso comercial proibido sem autorização expressa do autor.