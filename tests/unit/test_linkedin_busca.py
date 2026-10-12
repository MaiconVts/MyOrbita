"""
Busca do LinkedIn pelo endpoint guest seeMoreJobPostings (conferido ao vivo
em 12/10/2026): pagina de 10 em 10 via start, aceita até ~1000 resultados e
sinaliza o fim com um corpo vazio. A página /jobs/search parava em 60 vagas.

Defeitos anteriores cobertos aqui: modalidade gravada a partir da busca (e
não da vaga) e uma requisição por modalidade para as mesmas vagas.
"""
from types import SimpleNamespace

import pytest

from scrapers.linkedin_scraper import LinkedinScraper


def _card(id_vaga, local='São Paulo, SP'):
    return (
        '<li><div class="base-card job-search-card">'
        f'<a class="base-card__full-link" href="https://br.linkedin.com/jobs/view/advogado-{id_vaga}?trk=x">'
        '</a><h3 class="base-search-card__title">Advogado</h3>'
        '<h4 class="base-search-card__subtitle"><a>Escritório</a></h4>'
        f'<span class="job-search-card__location">{local}</span>'
        '<time class="job-search-card__listdate" datetime="2026-10-01"></time></div></li>'
    )


def _resposta(html):
    return SimpleNamespace(content=html.encode('utf-8'))


@pytest.fixture
def scraper(monkeypatch):
    instancia = LinkedinScraper()
    monkeypatch.setattr(instancia, '_aquecer_session', lambda: None)
    monkeypatch.setattr(instancia, '_delay_gaussiano', lambda *args: None)
    instancia.urls_pedidas = []
    return instancia


def _servir(scraper, monkeypatch, paginas):
    """Cada requisição devolve a próxima página da lista; depois, corpo vazio."""
    fila = list(paginas)

    def request_falso(url, pagina_interna=False, fragmento=False):
        scraper.urls_pedidas.append(url)
        if not fila:
            return _resposta('')
        pagina = fila.pop(0)
        return None if pagina is None else _resposta(pagina)

    monkeypatch.setattr(scraper, '_fazer_request', request_falso)


def test_pagina_ate_o_fim_e_sem_filtro_de_modalidade(scraper, monkeypatch):
    _servir(scraper, monkeypatch, [
        ''.join(_card(4000000000 + i) for i in range(10)),
        ''.join(_card(4000000100 + i) for i in range(3)),
    ])

    vagas = scraper.buscar_vagas('Advogado', 'Remoto', limite=300)

    assert len(vagas) == 13
    assert len(scraper.urls_pedidas) == 3
    assert 'start=0' in scraper.urls_pedidas[0]
    assert 'start=10' in scraper.urls_pedidas[1]
    assert all('f_WT' not in url for url in scraper.urls_pedidas)


def test_modalidade_vem_da_vaga_e_nao_da_busca(scraper, monkeypatch):
    _servir(scraper, monkeypatch, [_card(4000000001) + _card(4000000002, 'Brasil (Remoto)')])

    vagas = scraper.buscar_vagas('Advogado', 'Remoto', limite=300)

    assert sorted(v['modalidade'] for v in vagas) == ['Não informado', 'Remoto']


def test_para_apos_paginas_sem_vaga_inedita(scraper, monkeypatch):
    repetida = _card(4000000001)
    _servir(scraper, monkeypatch, [repetida] * 10)

    scraper.buscar_vagas('Advogado', 'Todas', limite=300)

    # 1ª página traz a vaga inédita; as 2 seguintes só repetem → para.
    assert len(scraper.urls_pedidas) == 1 + LinkedinScraper._MAX_PAGINAS_SEM_NOVIDADE


def test_limite_corta_a_lista_e_a_paginacao(scraper, monkeypatch):
    _servir(scraper, monkeypatch, [''.join(_card(4000000000 + i) for i in range(10))] * 5)

    assert len(scraper.buscar_vagas('Advogado', 'Todas', limite=5)) == 5
    assert len(scraper.urls_pedidas) == 1


def test_primeira_pagina_vazia_devolve_lista_vazia(scraper, monkeypatch):
    _servir(scraper, monkeypatch, [])

    assert scraper.buscar_vagas('Advogado', 'Todas', limite=300) == []


def test_falha_tenta_de_novo_uma_vez(scraper, monkeypatch):
    _servir(scraper, monkeypatch, [None, _card(4000000001)])

    assert len(scraper.buscar_vagas('Advogado', 'Todas', limite=300)) == 1


def test_duas_falhas_seguidas_encerram_a_busca(scraper, monkeypatch):
    _servir(scraper, monkeypatch, [None, None, _card(4000000001)])

    assert scraper.buscar_vagas('Advogado', 'Todas', limite=300) == []
    assert len(scraper.urls_pedidas) == 2
