"""
Busca do LinkedIn: a página /jobs/search ignora f_WT (modalidade) e start
(paginação) — conferido ao vivo em 05/10/2026: Remoto, Híbrido, Presencial e
start=25/60 devolvem as mesmas 60 vagas.

Defeito reproduzido: cada keyword fazia 2 requisições por modalidade (6 no
total) para as mesmas vagas, e todas eram gravadas com a modalidade da
primeira busca ('Remoto').
"""
from types import SimpleNamespace

import pytest

from scrapers.linkedin_scraper import LinkedinScraper


def _card(id_vaga, local):
    return (
        '<li><div class="base-card job-search-card">'
        f'<a class="base-card__full-link" href="https://br.linkedin.com/jobs/view/advogado-{id_vaga}?trk=x">'
        '</a><h3 class="base-search-card__title">Advogado</h3>'
        '<h4 class="base-search-card__subtitle"><a>Escritório</a></h4>'
        f'<span class="job-search-card__location">{local}</span>'
        '<time class="job-search-card__listdate" datetime="2026-10-01"></time></div></li>'
    )


@pytest.fixture
def scraper(monkeypatch):
    instancia = LinkedinScraper()
    urls = []
    pagina = ''.join([_card(4000000001, 'São Paulo, SP'), _card(4000000002, 'Brasil (Remoto)')])

    def request_falso(url, pagina_interna=False):
        urls.append(url)
        return SimpleNamespace(content=pagina.encode('utf-8'))

    monkeypatch.setattr(instancia, '_fazer_request', request_falso)
    monkeypatch.setattr(instancia, '_aquecer_session', lambda: None)
    monkeypatch.setattr(instancia, '_delay_gaussiano', lambda *args: None)
    instancia.urls_pedidas = urls
    return instancia


def test_uma_requisicao_por_keyword_e_sem_filtro_de_modalidade(scraper):
    scraper.buscar_vagas('Advogado', 'Remoto', limite=120)

    assert len(scraper.urls_pedidas) == 1
    assert 'f_WT' not in scraper.urls_pedidas[0]


def test_modalidade_vem_da_vaga_e_nao_da_busca(scraper):
    vagas = scraper.buscar_vagas('Advogado', 'Remoto', limite=120)

    assert sorted(v['modalidade'] for v in vagas) == ['Não informado', 'Remoto']


def test_pagina_sem_vagas_devolve_lista_vazia(scraper, monkeypatch):
    monkeypatch.setattr(scraper, '_fazer_request', lambda url, pagina_interna=False: SimpleNamespace(content=b'<html></html>'))

    assert scraper.buscar_vagas('Advogado', 'Todas', limite=120) == []


def test_limite_corta_a_lista(scraper):
    assert len(scraper.buscar_vagas('Advogado', 'Todas', limite=1)) == 1


def test_busca_que_falha_devolve_lista_vazia(scraper, monkeypatch):
    monkeypatch.setattr(scraper, '_fazer_request', lambda url, pagina_interna=False: None)

    assert scraper.buscar_vagas('Advogado', 'Todas', limite=120) == []
