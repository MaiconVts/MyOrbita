"""
Filtro de relevância do runner.

Defeitos reproduzidos (12/10/2026):
- 'de' em 'Analista de Dados' casava com quase qualquer título;
- no ADV, a vaga só passava se o título tivesse um termo da keyword que a
  trouxe ('Advogado' rejeitava 'Analista Jurídico'); agora vale o domínio.
"""
import json
from pathlib import Path

from scraper_runner import _filtrar_por_relevancia, _termos_da_keyword, extrair_parametros

RAIZ = Path(__file__).resolve().parents[2]


def _titulos(*titulos):
    return [{'titulo': t} for t in titulos]


def test_preposicao_nao_conta_como_termo():
    assert _termos_da_keyword('Analista de Dados') == ['analista', 'dados']


def test_termos_dominio_do_adv():
    config = json.loads((RAIZ / 'queries' / 'advogados_linkedin.json').read_text(encoding='utf-8'))
    termos = extrair_parametros(config)['termos_dominio']

    aceitas, rejeitadas = _filtrar_por_relevancia(_titulos(
        'Analista Jurídico Pleno',
        'Estagiária de Direito',
        'Advogada Trabalhista',
        'Legal Counsel',
        'DPO - Encarregado de Dados',
        'Vendedor Interno',
        'Analista de Dados',
    ), termos)

    assert [v['titulo'] for v in aceitas] == [
        'Analista Jurídico Pleno', 'Estagiária de Direito', 'Advogada Trabalhista',
        'Legal Counsel', 'DPO - Encarregado de Dados',
    ]
    assert rejeitadas == 2
