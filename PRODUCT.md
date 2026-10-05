# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
Profissionais brasileiros procurando emprego em duas áreas: **tecnologia** (desenvolvimento) e **direito** (advocacia e jurídico). Chegam com uma tarefa clara: ver de uma vez as vagas novas da sua área, filtrar pelo que importa (modalidade, estado, nível, contrato, origem) e sair para a candidatura na plataforma de origem. Voltam com frequência, porque a lista muda todo dia.

O site também é portfólio técnico do autor, mas isso é secundário: a interface serve o candidato, e o portfólio aparece no Sobre e no crédito do rodapé.

## Product Purpose
Buscar vaga exige abrir várias plataformas, cada uma com sua interface e seus limites. O MyOrbita coleta vagas automaticamente todos os dias, padroniza os dados e serve tudo numa interface única, com filtros que as plataformas não oferecem de forma consolidada. Dá certo quando o candidato encontra uma vaga relevante em poucos minutos e clica para se candidatar na origem.

## Positioning
Um agregador diário e gratuito, focado em duas áreas (tech e jurídico) e com **foco em vagas remotas**. Vagas híbridas e presenciais também aparecem e podem ser filtradas. O MyOrbita não hospeda candidaturas: leva o candidato à vaga original.

## Operating Context
- Coleta diária por GitHub Actions (scrapers em Python) gravando no Firebase Realtime Database; o frontend lê pelo SDK do Firebase com cache local de 1h.
- Fontes: Gupy e LinkedIn. **Em 05/10/2026 o Gupy está fora do ar** (rotas vazias desde 01/10); o conserto do backend vem em seguida. O texto público continua citando Gupy e LinkedIn.
- Rotas do site: `/` (escolha da área), `/vagas-dev`, `/vagas-adv`. Cerca de 2 mil vagas por área hoje.
- Deploy na Vercel ([my-orbita.vercel.app](https://my-orbita.vercel.app/)).

## Capabilities and Constraints
- Filtros por modalidade, estado, nível, tipo de contrato e origem; detalhe da vaga com link para a vaga original.
- Muitos campos chegam como "Não informado" (tipo de contrato em 68% das vagas DEV e 91% das ADV); a interface precisa lidar com dado ausente sem parecer quebrada.
- Stack: React 19 + Vite + Tailwind 4, React Router, Zustand, Firebase. SPA na Vercel.
- **SEO é requisito:** o site precisa ser encontrável em buscas por vagas de tecnologia e de direito (metadados por rota, título e descrição, Open Graph, sitemap e robots, dados estruturados quando couber).
- Decisão aberta: botão "me pague um café" no rodapé com link do PayPal. Falta o link; não inventar.

## Brand Commitments
- Nome **MyOrbita**: o tema órbita/espaço é central à marca e já levou a refazer o projeto inteiro uma vez.
- O dono quer manter o jogo de cores atual (fundo espacial em roxo profundo, âmbar `#FFB703` e azul elétrico `#4FC3F7`, estrelas coloridas), os efeitos e as animações de sistema planetário. O resto do estilo pode mudar por completo.
- Tech associado ao azul elétrico e jurídico ao âmbar.
- Idioma: português do Brasil.

## Evidence on Hand
- Contagens reais de vagas vindas do Firebase (podem ser exibidas calculadas a partir dos dados).
- Ícone de órbita em `myorbita-web/public/solar-system-orbit-svgrepo-com.svg`.
- Textos de Termos, Privacidade, Sobre, Como Usar e Como Funciona em `myorbita-web/src/components/modals/`.
- Não há depoimentos, usuários citáveis, métricas de uso nem imprensa. Não fabricar.

## Product Principles
1. **A vaga é o produto.** Tudo o que atrasa o candidato entre abrir o site e chegar a uma vaga relevante é custo.
2. **Dado honesto.** Contagens, fontes e datas vêm dos dados reais; campo ausente aparece como ausente, sem inventar.
3. **Duas áreas, uma casa.** Tech e jurídico compartilham a mesma estrutura e se distinguem pela cor de identidade.
4. **Encontrável.** Cada rota de vagas deve poder ser achada e entendida por buscadores e por quem recebe o link.

## Accessibility & Inclusion
Contraste AA, inclusive sobre o fundo animado; foco visível; navegação por teclado nos filtros e modais; `prefers-reduced-motion` respeitado; uso confortável no celular.
