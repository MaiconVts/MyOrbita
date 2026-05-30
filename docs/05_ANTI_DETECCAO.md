# 05 — Anti-Detecção LinkedIn

> Última atualização: Maio/2026

---

## Contexto

O LinkedIn utiliza Cloudflare e heurísticas próprias para detectar bots. O scraper acessa apenas páginas públicas, sem autenticação, o que exige um conjunto de camadas de proteção para manter uma taxa de sucesso estável sem gerar ban.

---

## 12 Camadas de Proteção

| # | Camada | Descrição |
|---|---|---|
| 1 | **TLS Fingerprint** | `curl_cffi` com `impersonate="chrome"` replica o handshake JA3/HTTP2 idêntico ao Chrome real |
| 2 | **Session Persistente** | Cookies mantidos entre requests como um navegador real |
| 3 | **Warm-up 3 etapas** | Google → Homepage → /jobs/ antes de qualquer busca, coletando cookies naturalmente |
| 4 | **Headers Sec-Fetch** | `Sec-Fetch-Dest`, `Sec-Fetch-Mode`, `Sec-Fetch-Site` — enviados por navegadores modernos, ignorados por bots |
| 5 | **Rotação User-Agent** | 5 variações de Chrome em Windows, macOS e Linux |
| 6 | **Delays Gaussianos** | `random.gauss()` com clamp — humanos têm distribuição em sino, não uniforme |
| 7 | **Cooldown entre Keywords** | Pausa adicional ao trocar de palavra-chave |
| 8 | **Detecção de Bloqueio** | Verifica authwall, `/challenge/` e tamanho anômalo do response |
| 9 | **Circuit Breaker** | 5 erros consecutivos → abort automático. Taxa de erro > 20% → pausa de 120s |
| 10 | **Teto Global** | Máximo de requests por execução como margem de segurança contra loops |
| 11 | **Referer Chain** | Cada request tem o referer da página anterior |
| 12 | **UTF-8 Forçado** | Bytes do response decodificados explicitamente como UTF-8, eliminando mojibake |

---

## Filtros Validados

Os parâmetros de filtro do LinkedIn foram validados empiricamente — os conjuntos de vagas retornados são 100% disjuntos entre si:

| Parâmetro | Valor | Resultado |
|---|---|---|
| `f_WT=1` | Presencial | Só vagas presenciais |
| `f_WT=2` | Remoto | Só vagas remotas |
| `f_WT=3` | Híbrido | Só vagas híbridas |

---

## Lições Aprendidas

**Sinais de bloqueio falso-positivo** — a palavra `recaptcha` aparece no HTML de páginas válidas como script preventivo. Usar ela como sinal de bloqueio gerava falso-positivo em 100% das requisições. Apenas `authwall`, `/challenge/` e `checkpoint/challenge` são sinais confiáveis.

**Teto global é margem de segurança, não limitador** — o teto de requests deve ser calculado acima do volume normal de execução. Um teto muito baixo mata execuções inteiras silenciosamente. A proteção real contra ban é o circuit breaker + detecção de bloqueio.

**Pausa após última página é redundante** — a pausa longa entre páginas da mesma keyword protege contra detecção. Após a última página, a próxima ação já é uma nova keyword (URL diferente), que por si só representa uma transição natural. Eliminar a pausa final economiza tempo sem perda de proteção.

**Enriquecedor desacoplado** — buscar tipo_contrato na página interna de cada card durante a listagem multiplica o volume de requests por 60x por página. O LinkedIn detecta esse padrão rapidamente. A solução foi desacoplar em um job separado que roda após a coleta.
