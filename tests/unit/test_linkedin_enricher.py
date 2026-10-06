"""
Enriquecedor: escolha das vagas pendentes e marcação da tentativa.

Defeito reproduzido: a vaga cuja página não informa o contrato continuava
"Não informado" e voltava como pendente em toda execução, ocupando as
mesmas 200 vagas do limite diário.
"""
from datetime import UTC, datetime, timedelta

import pytest

from scrapers import linkedin_enricher
from scrapers.linkedin_enricher import LinkedinEnricher, selecionar_pendentes

AGORA = datetime(2026, 10, 5, 22, 0, tzinfo=UTC)
ROTA = '/vagas/dev/linkedin'


def _vaga(link='https://br.linkedin.com/jobs/view/1', contrato='Não informado', verificado_em=None):
    vaga = {'titulo': 'Dev', 'link': link, 'tipo_contrato': contrato}
    if verificado_em is not None:
        vaga['contrato_verificado_em'] = verificado_em
    return vaga


class _RefFalsa:
    """Substitui db.reference: guarda o snapshot e registra os update()."""

    def __init__(self, banco, caminho):
        self._banco = banco
        self._caminho = caminho

    def get(self):
        return self._banco['snapshot']

    def update(self, dados):
        self._banco['updates'].append((self._caminho, dados))


@pytest.fixture
def banco(monkeypatch):
    estado = {'snapshot': {}, 'updates': []}
    monkeypatch.setattr(linkedin_enricher.db, 'reference', lambda caminho: _RefFalsa(estado, caminho))
    return estado


@pytest.fixture
def enricher(monkeypatch):
    instancia = LinkedinEnricher()
    monkeypatch.setattr(instancia, '_aquecer_session', lambda: None)
    monkeypatch.setattr(instancia, '_circuit_breaker_aberto', lambda: False)
    return instancia


# ---------------------------------------------------------------- defeito


def test_vaga_ja_tentada_sem_contrato_nao_volta_na_execucao_seguinte(banco, enricher, monkeypatch):
    banco['snapshot'] = {'a': _vaga()}
    monkeypatch.setattr(enricher, '_extrair_contrato_pagina_interna', lambda link: 'Não informado')

    enricher.enriquecer_rota(ROTA, limite=10)
    caminho, dados = banco['updates'][-1]
    banco['snapshot']['a'].update(dados)

    assert caminho == f'{ROTA}/a'
    assert 'contrato_verificado_em' in dados
    assert enricher._carregar_pendentes(ROTA, limite=10) == {}


# ---------------------------------------------------------------- enriquecer_rota


def test_contrato_encontrado_grava_so_o_contrato(banco, enricher, monkeypatch):
    banco['snapshot'] = {'a': _vaga()}
    monkeypatch.setattr(enricher, '_extrair_contrato_pagina_interna', lambda link: 'CLT')

    enricher.enriquecer_rota(ROTA, limite=10)

    assert banco['updates'] == [(f'{ROTA}/a', {'tipo_contrato': 'CLT'})]


def test_falha_de_requisicao_nao_marca_a_tentativa(banco, enricher, monkeypatch):
    banco['snapshot'] = {'a': _vaga()}
    monkeypatch.setattr(enricher, '_extrair_contrato_pagina_interna', lambda link: None)

    enricher.enriquecer_rota(ROTA, limite=10)

    assert banco['updates'] == []


def test_pagina_interna_devolve_none_quando_a_requisicao_falha(enricher, monkeypatch):
    monkeypatch.setattr(enricher, '_delay_gaussiano', lambda *args: None)
    monkeypatch.setattr(enricher, '_fazer_request', lambda link, pagina_interna=False: None)

    assert enricher._extrair_contrato_pagina_interna('https://br.linkedin.com/jobs/view/1') is None


# ---------------------------------------------------------------- selecionar_pendentes


def test_pula_tentada_dentro_da_janela_e_reabre_depois_dela():
    snapshot = {
        'recente': _vaga(verificado_em=(AGORA - timedelta(days=1)).isoformat()),
        'antiga': _vaga(verificado_em=(AGORA - timedelta(days=8)).isoformat()),
    }

    assert list(selecionar_pendentes(snapshot, limite=10, agora=AGORA)) == ['antiga']


def test_nunca_tentadas_vem_antes_das_reabertas_quando_o_limite_corta():
    snapshot = {
        'reaberta': _vaga(verificado_em=(AGORA - timedelta(days=30)).isoformat()),
        'nova_1': _vaga(),
        'nova_2': _vaga(),
    }

    assert list(selecionar_pendentes(snapshot, limite=2, agora=AGORA)) == ['nova_1', 'nova_2']


def test_ignora_contrato_preenchido_vaga_sem_link_e_item_que_nao_e_vaga():
    snapshot = {
        'com_contrato': _vaga(contrato='CLT'),
        'sem_link': _vaga(link=''),
        'lixo': 'texto solto',
        'ok': _vaga(),
    }

    assert list(selecionar_pendentes(snapshot, limite=10, agora=AGORA)) == ['ok']


@pytest.mark.parametrize('valor', ['ontem', '', 123, None])
def test_data_de_verificacao_invalida_conta_como_nunca_tentada(valor):
    snapshot = {'a': {**_vaga(), 'contrato_verificado_em': valor}}

    assert list(selecionar_pendentes(snapshot, limite=10, agora=AGORA)) == ['a']


@pytest.mark.parametrize('snapshot', [None, {}, [], 'x'])
def test_snapshot_vazio_ou_invalido_nao_tem_pendentes(snapshot):
    assert selecionar_pendentes(snapshot, limite=10, agora=AGORA) == {}


# ---------------------------------------------------------------- falhas do banco


def test_falha_ao_ler_a_rota_devolve_none_em_vez_de_nenhuma_pendente(enricher, monkeypatch):
    def reference_quebrada(caminho):
        raise ConnectionError('sem rede')

    monkeypatch.setattr(linkedin_enricher.db, 'reference', reference_quebrada)

    assert enricher.enriquecer_rota(ROTA, limite=10) is None


def test_rota_sem_pendentes_devolve_resumo_zerado(banco, enricher):
    resumo = enricher.enriquecer_rota(ROTA, limite=10)

    assert resumo == {'atualizadas': 0, 'sem_contrato': 0, 'falhas_requisicao': 0, 'falhas_gravacao': 0}


def test_falha_ao_gravar_conta_como_falha_de_gravacao_e_nao_como_atualizada(banco, enricher, monkeypatch):
    banco['snapshot'] = {'a': _vaga(), 'b': _vaga()}
    monkeypatch.setattr(enricher, '_extrair_contrato_pagina_interna', lambda link: 'CLT')

    def update_quebrado(self, dados):
        raise ConnectionError('sem rede')

    monkeypatch.setattr(_RefFalsa, 'update', update_quebrado)

    resumo = enricher.enriquecer_rota(ROTA, limite=10)

    assert resumo == {'atualizadas': 0, 'sem_contrato': 0, 'falhas_requisicao': 0, 'falhas_gravacao': 2}
