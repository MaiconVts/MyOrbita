# 01 — Contexto do Projeto

> Última atualização: Maio/2026

---

## O que é

MyOrbita é um agregador de vagas profissionais desenvolvido como projeto solo de portfólio técnico. O objetivo é reunir vagas de múltiplas plataformas em um lugar só, com filtros eficazes e interface limpa — algo que as próprias plataformas de emprego não oferecem de forma consolidada para nichos específicos.

O sistema coleta vagas automaticamente todos os dias, padroniza os dados e os serve em uma interface web organizada por categoria profissional.

---

## Problema

Buscar vagas exige acessar múltiplas plataformas manualmente, cada uma com sua própria interface, filtros e limitações. Não existe hoje uma ferramenta gratuita que consolide vagas de Gupy e LinkedIn em um único lugar, com filtros combinados por modalidade, estado, nível, contrato e origem.

---

## Solução

Um sistema autônomo que roda diariamente via GitHub Actions, coleta vagas das plataformas alvo, padroniza os dados e os disponibiliza em uma interface web com filtros avançados. O usuário acessa um único lugar e encontra vagas de todas as fontes integradas.

---

## Categorias e Fontes

| Categoria | Fonte | Status |
|---|---|---|
| Tecnologia | Gupy | ✅ Em produção |
| Tecnologia | LinkedIn | ✅ Em produção |
| Direito | Gupy | ✅ Em produção |
| Direito | LinkedIn | ✅ Em produção |

---

## Plataformas

| Plataforma | Status |
|---|---|
| Web (React + Vite) | ✅ Funcional, deploy pendente |
| Mobile (React Native + Expo) | 📋 Planejado |

---

## Decisões de Escopo

**Uso pessoal e portfólio** — o projeto não tem fins comerciais. Foi desenvolvido para uso próprio e como demonstração técnica.

**Monorepo** — scrapers, web e mobile no mesmo repositório. Simplicidade de manutenção para um projeto solo.

**Custo zero** — toda a stack é gratuita: Firebase Spark, GitHub Actions free tier, Vercel free tier. O projeto não gera custo operacional.

**Duas categorias** — Tecnologia e Direito foram escolhidas por proximidade com o contexto pessoal do autor. A arquitetura permite adicionar novas categorias com alterações mínimas.

---

## Limitações Conhecidas

- **Dados do LinkedIn incompletos** — o LinkedIn não expõe uma API pública. O scraper acessa HTML público, o que significa que campos como `tipo_contrato` e `state` nem sempre estão disponíveis na listagem. Um job separado (enriquecedor) tenta preencher esses campos acessando a página interna de cada vaga.

- **Vagas sem localização precisa** — quando o LinkedIn retorna apenas "Cidade, Brasil" sem UF, o sistema infere o estado por um mapa de cidades conhecidas. Cidades não mapeadas ficam com `state` ausente.

- **Cobertura parcial do LinkedIn** — o scraper respeita limites anti-detecção (delays, circuit breaker, teto de requests). Isso garante estabilidade mas limita o volume coletado por execução.

- **Sem autenticação** — o sistema acessa apenas vagas públicas. Vagas restritas a usuários logados não são coletadas.

- **Firebase Realtime DB** — cada execução sobrescreve os dados da rota com o snapshot mais recente. Vagas expiradas saem naturalmente, mas uma execução local interrompida no meio pode deixar dados parciais até a próxima execução agendada.

---

## O que não é

- Não é um sistema de candidatura — apenas agrega e exibe vagas com link para a fonte original.
- Não é um sistema de alertas ou notificações — exibição passiva via interface web.
- Não substitui as plataformas originais — é uma camada de consolidação sobre elas.
