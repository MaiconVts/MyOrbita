# 03 — Dados

> Última atualização: Maio/2026

---

## Interface IVaga

Contrato de dados compartilhado entre backend e frontend. Todo scraper deve produzir um dicionário com essas chaves — `padronizar_vaga()` em `BaseScraper` garante isso.

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `id` | string | ✅ | Hash MD5 da URL (16 chars) |
| `titulo` | string | ✅ | Título da vaga |
| `empresa` | string | ✅ | Nome da empresa |
| `modalidade` | string | ✅ | Remoto / Híbrido / Presencial |
| `link` | string | ✅ | URL da vaga na plataforma original |
| `data_publicacao` | string | ✅ | ISO 8601 |
| `origem` | string | ✅ | Gupy / LinkedIn |
| `city` | string | — | Cidade |
| `state` | string | — | Sigla UF (SP, MG, RJ...) |
| `country` | string | — | País (default: Brasil) |
| `is_remote` | boolean | — | true se modalidade for Remoto |
| `tipo_contrato` | string | — | CLT / PJ / Estágio / Temporário / Trainee / Voluntário |
| `prazo_inscricao` | string | — | ISO 8601 — só Gupy |
| `pcd` | boolean | — | true se vaga inclusiva — só Gupy |
| `workplace_type` | string | — | Valor bruto da API Gupy |

Campos ausentes chegam como `"Não informado"` após normalização. O frontend trata esses valores com permissividade nos filtros e indicador visual no card.

---

## Normalização

Todo campo textual passa por `_normalizar_campo()` antes de ser salvo:

- `None` → `"Não informado"`
- String vazia ou só espaços → `"Não informado"`
- String válida → aplicado `strip()` + correção de mojibake
- Booleanos e números passam direto

Estados brasileiros passam por `_normalizar_estado()` que converte nome completo para sigla UF. Nomes desconhecidos retornam o valor original.

### Correção de Mojibake
Quando bytes UTF-8 são interpretados como Latin-1 e reencodados, caracteres acentuados viram lixo (`"Estágio"` → `"EstÃ¡gio"`). O helper `consertar_mojibake()` reverte esse dano via `encode('latin-1').decode('utf-8')` e é aplicado em todos os campos textuais como rede de proteção.

---

## ID Determinístico

```python
hashlib.md5(link.encode('utf-8')).hexdigest()[:16]
```

O ID é sempre o mesmo para a mesma URL. Isso garante:
- Deduplicação sem lookup externo
- Atualização idempotente no Firebase
- Rastreabilidade entre execuções

---

## Mapeamentos

### Tipo de Contrato — LinkedIn
O LinkedIn expõe `employmentType` no JSON-LD da página interna e texto legível no HTML. Ambas as fontes são tentadas:

| Valor bruto | Tradução |
|---|---|
| `full_time` / `full-time` / `tempo integral` | CLT |
| `part_time` / `part-time` / `meio período` | Meio período |
| `internship` / `estágio` | Estágio |
| `contract` / `autônomo` | PJ |
| `temporary` / `temporário` | Temporário |
| `trainee` | Trainee |
| `volunteer` / `voluntário` | Voluntário |

### Tipo de Contrato — Gupy
A API Gupy retorna códigos internos que são mapeados para português:

| Código Gupy | Tradução |
|---|---|
| `vacancy_type_effective` | CLT |
| `vacancy_type_internship` | Estágio |
| `vacancy_type_independent_contractor` | PJ |
| `vacancy_legal_entity` | PJ |
| `vacancy_type_trainee` | Trainee |
| `vacancy_type_outsource` | Terceirizado |
| `vacancy_type_lecturer` | Professor |

### Modalidade — LinkedIn
| Valor bruto | Tradução |
|---|---|
| `remote` / `remoto` | Remoto |
| `on-site` / `presencial` | Presencial |
| `hybrid` / `híbrido` / `hibrido` | Híbrido |

---

## Localização LinkedIn

O LinkedIn retorna localização em texto livre. O parser `_parse_localizacao()` cobre os formatos conhecidos:

| Formato recebido | Resultado |
|---|---|
| `"São Paulo, São Paulo, Brasil"` | city=São Paulo, state=SP, country=Brasil |
| `"São Paulo, Brasil"` | city=São Paulo, state=SP (inferido), country=Brasil |
| `"Brasil"` | city=None, state=None, country=Brasil |
| `None` | city=None, state=None, country=None |

Quando o estado não vem explícito, é inferido pelo nome da cidade via `_CIDADE_PARA_UF` — um mapa com as principais cidades brasileiras. Cidades não mapeadas ficam com `state: "Não informado"`.

---

## Rotas Firebase

```
/vagas/dev/gupy      → {id: IVaga, ...}
/vagas/dev/linkedin  → {id: IVaga, ...}
/vagas/adv/gupy      → {id: IVaga, ...}
/vagas/adv/linkedin  → {id: IVaga, ...}
```

Cada rota é um hashmap com o ID da vaga como chave. Estrutura flat — sem aninhamento — para leitura eficiente via Firebase REST.
