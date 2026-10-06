"""
scraper_runner.py — Orquestração compartilhada entre todas as plataformas.

Responsabilidade Única: coordenar o fluxo de execução de um scraper qualquer.
- Configura logging UTF-8 (Windows + Linux)
- Inicializa Firebase
- Carrega queries da categoria (dev/adv)
- Executa buscas com deduplicação 3 níveis
- Grava cada combinação no Firebase via update() (merge, nunca set())
- No fim, remove as vagas expiradas só se a coleta foi saudável;
  senão, falha o job (exit 1)
- Imprime métricas

Cada main (main_gupy, main_linkedin) importa daqui e só precisa:
1. Instanciar seu scraper
2. Definir o nome da plataforma
3. Chamar executar()

Toda a plumbing fica aqui, DRY ao máximo.
"""
import json
import logging
import os
import re
import sys
import time
import unicodedata
from typing import Protocol

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, db

load_dotenv()

# ============================================================
# LOGGING — UTF-8 forçado para Windows + Linux
# ============================================================
_logging_configurado = False


def configurar_logging():
    """Configura logging uma única vez, mesmo se chamado múltiplas vezes."""
    global _logging_configurado
    if _logging_configurado:
        return

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )

    file_handler = logging.FileHandler('scraper.log', mode='w', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(
        open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False)
    )
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    _logging_configurado = True


logger = logging.getLogger(__name__)


# ============================================================
# PROTOCOLO DO SCRAPER — tipagem estrutural (Duck Typing formal)
# ============================================================
class ScraperProtocol(Protocol):
    """
    Qualquer objeto que tenha o método buscar_vagas com essa assinatura
    pode ser usado pelo runner. Não precisa herdar nada.
    """
    def buscar_vagas(self, palavra_chave: str, modalidade: str, limite: int) -> list: ...


# ============================================================
# CONFIGURAÇÃO FIREBASE
# ============================================================
FIREBASE_KEY_PATH = os.getenv("FIREBASE_KEY_PATH")
FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL")
# Tempo limite (s) de cada chamada HTTP do SDK ao Firebase; o padrão do SDK é 120s.
FIREBASE_HTTP_TIMEOUT_S = 60


def inicializar_firebase():
    """Inicializa Firebase uma única vez (idempotente)."""
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_KEY_PATH)
        firebase_admin.initialize_app(cred, {
            'databaseURL': FIREBASE_DB_URL,
            'httpTimeout': FIREBASE_HTTP_TIMEOUT_S,
        })
        logger.info("Conexão com Firebase inicializada com sucesso!")


def carregar_snapshot_firebase(rota: str) -> dict:
    """
    Carrega snapshot completo do Firebase antes do scraping.
    Usado para deduplicação (set de IDs) e para preservar campos já
    enriquecidos pelo enricher (tipo_contrato) que o ref.set() do scraper
    sobrescreveria com 'Não informado'.
    """
    try:
        ref = db.reference(rota)
        snapshot = ref.get()
        if snapshot and isinstance(snapshot, dict):
            logger.info(f"Cache Firebase: {len(snapshot)} vagas já existentes em '{rota}'")
            return snapshot
        return {}
    except Exception as e:
        logger.warning(f"Falha ao carregar cache do Firebase '{rota}': {e}")
        return {}


_CONTRATO_VAZIO = ('Não informado', '', None)
_TAMANHO_LOTE_FIREBASE = 500


def _montar_payload(lista_vagas: list, ids_existentes: set) -> dict:
    """
    Monta o payload multi-caminho do update().

    Vaga nova entra inteira. Vaga que já existe é gravada campo a campo
    ('id/campo') e, se o scraper não achou contrato, o campo tipo_contrato
    fica de fora — assim o valor gravado pelo enricher (mesmo durante
    esta execução) não volta para 'Não informado'.
    """
    payload = {}
    for vaga in lista_vagas:
        id_vaga = vaga['id']
        if id_vaga not in ids_existentes:
            payload[id_vaga] = vaga
            continue
        for campo, valor in vaga.items():
            if campo == 'tipo_contrato' and valor in _CONTRATO_VAZIO:
                continue
            payload[f"{id_vaga}/{campo}"] = valor
    return payload


def _atualizar_em_lotes(rota: str, payload: dict):
    """update() em lotes, para não mandar um PATCH gigante de uma vez."""
    ref = db.reference(rota)
    chaves = list(payload.keys())
    for i in range(0, len(chaves), _TAMANHO_LOTE_FIREBASE):
        ref.update({k: payload[k] for k in chaves[i:i + _TAMANHO_LOTE_FIREBASE]})


def enviar_para_firebase(lista_vagas: list, rota: str, ids_existentes: set) -> bool:
    """
    Grava vagas na rota via update() (merge), nunca via set().

    O set() trocava a rota inteira pelo que a execução tinha acumulado até
    ali: o site via rota parcial durante a coleta, e uma lista vazia
    apagava a rota (foi o que aconteceu com a Gupy em 01/10). Com update(),
    a rota só ganha ou atualiza vagas; as expiradas saem em remover_expiradas().
    """
    if not lista_vagas:
        logger.warning(f"[FIREBASE]: lista vazia para '{rota}', nada enviado.")
        return False
    try:
        _atualizar_em_lotes(rota, _montar_payload(lista_vagas, ids_existentes))
        logger.info(f"[FIREBASE]: {len(lista_vagas)} vagas gravadas em '{rota}'.")
        return True
    except Exception as e:
        logger.error(f"[FIREBASE ERRO]: Falha ao enviar dados. Erro: {str(e)}")
        return False


def remover_expiradas(ids_coletados: set, ids_existentes: set, rota: str) -> int:
    """Apaga da rota as vagas do snapshot inicial que não apareceram nesta execução."""
    expiradas = ids_existentes - ids_coletados
    if not expiradas:
        return 0
    try:
        _atualizar_em_lotes(rota, {id_vaga: None for id_vaga in expiradas})
        logger.info(f"[FIREBASE]: {len(expiradas)} vagas expiradas removidas de '{rota}'.")
        return len(expiradas)
    except Exception as e:
        logger.error(f"[FIREBASE ERRO]: Falha ao remover expiradas. Erro: {str(e)}")
        return 0


# ============================================================
# CONFIGURAÇÕES DE QUERIES
# ============================================================
# Abaixo disso a coleta é tratada como quebrada: o job falha (exit 1) e as
# vagas expiradas não são removidas. Sobrescreva por categoria com
# configuracoes_gerais.minimo_vagas no JSON de queries.
MINIMO_VAGAS_PADRAO = 50
# Coleta menor que esta fração do snapshot inicial também conta como quebrada
# (ex.: bloqueio do LinkedIn no meio da execução), para não esvaziar a rota.
PROPORCAO_MINIMA_SNAPSHOT = 0.5


def carregar_configuracoes(arquivo_queries: str):
    """Lê JSON de queries da categoria."""
    try:
        with open(arquivo_queries, 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        logger.error(f"O arquivo '{arquivo_queries}' não foi encontrado.")
        return None


def extrair_parametros(config: dict) -> dict:
    """Normaliza a estrutura do JSON de queries."""
    return {
        'palavras_chave': config['filtros_de_busca']['palavras_chave'],
        'modalidades': config['filtros_de_busca']['modalidades'],
        'limite_busca': config['configuracoes_gerais']['limite_vagas_por_pesquisa'],
        'minimo_vagas': config['configuracoes_gerais'].get('minimo_vagas', MINIMO_VAGAS_PADRAO),
    }


def exibir_info_configuracoes(parametros: dict, plataforma: str):
    """Log das configurações carregadas."""
    total_combinacoes = len(parametros['palavras_chave']) * len(parametros['modalidades'])
    logger.info(f"Configurações: {len(parametros['palavras_chave'])} palavras-chave × "
                f"{len(parametros['modalidades'])} modalidades = {total_combinacoes} combinações")
    logger.info(f"Limite por busca: {parametros['limite_busca']} vagas (uma requisição por palavra no LinkedIn)")
    logger.info(f"Plataforma alvo: {plataforma.upper()}")
    logger.info("-" * 60)


# ============================================================
# FILTRO DE RELEVÂNCIA — protege contra resultados degradados do LinkedIn
# ============================================================

def _normalizar_para_filtro(texto: str) -> str:
    """Remove acentos, pontuação e converte para minúsculas."""
    sem_acento = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    return re.sub(r'[^a-z0-9]', ' ', sem_acento.lower())


def _termos_da_keyword(keyword: str, min_len: int = 2) -> list[str]:
    """
    Extrai palavras significativas da keyword (>= min_len chars).
    Ex: 'Desenvolvedor Front-end' → ['desenvolvedor', 'front', 'end']
        'C#' → []  (sem termos válidos → filtro desativado para esta keyword)
    """
    return [w for w in _normalizar_para_filtro(keyword).split() if len(w) >= min_len]


def _filtrar_por_relevancia(vagas: list, termos_keyword: list[str]) -> tuple[list, int]:
    """
    Rejeita vagas cujo título não contém nenhum termo da keyword que as gerou.

    Termos curtos (≤ 3 chars: 'ti', 'qa', 'aws') usam match de palavra inteira
    para não casar como substring de outra palavra (ex: 'ti' em 'marketing').
    Termos longos usam substring — mais rápido e suficientemente preciso.

    Keywords sem termos válidos (ex: 'C', 'C#') desativam o filtro e aceitam tudo.
    """
    if not termos_keyword:
        return vagas, 0

    aceitas = []
    rejeitadas = 0

    for vaga in vagas:
        titulo_norm = _normalizar_para_filtro(vaga.get('titulo') or '')
        titulo_padded = f' {titulo_norm} '

        encontrou = any(
            (f' {t} ' in titulo_padded) if len(t) <= 3 else (t in titulo_norm)
            for t in termos_keyword
        )

        if encontrou:
            aceitas.append(vaga)
        else:
            rejeitadas += 1
            logger.warning(
                f"[RELEVÂNCIA] Fora do escopo — '{vaga.get('titulo', '?')}' "
                f"(nenhum termo de '{' '.join(termos_keyword)}' no título)"
            )

    return aceitas, rejeitadas


# ============================================================
# DEDUPLICAÇÃO 3 NÍVEIS
# ============================================================
def filtrar_duplicadas(vagas: list, urls_vistas: set, ids_firebase: set) -> tuple:
    """
    Deduplicação 3 níveis:
    1. URL já vista nesta execução (duplicata intra-scraping)
    2. ID já existe no Firebase (duplicata cross-execução — ainda adiciona
       pro ref.set() final sobrescrever com dados atualizados)
    3. Vaga genuinamente nova — adiciona
    """
    vagas_unicas = []
    duplicadas = 0
    ja_firebase = 0

    for vaga in vagas:
        if vaga['link'] in urls_vistas:
            duplicadas += 1
            continue
        urls_vistas.add(vaga['link'])

        if vaga['id'] in ids_firebase:
            ja_firebase += 1
            vagas_unicas.append(vaga)
            continue

        vagas_unicas.append(vaga)

    return vagas_unicas, duplicadas, ja_firebase


# ============================================================
# LOOP PRINCIPAL DE BUSCAS
# ============================================================
def executar_buscas(scraper: ScraperProtocol, parametros: dict, snapshot_firebase: dict, rota: str) -> dict:
    """
    Loop de buscas: itera palavras × modalidades, aplica dedup e grava
    cada combinação no Firebase via update() (merge). Um timeout no
    GitHub Actions perde no máximo a combinação em andamento.
    """
    ids_firebase = set(snapshot_firebase.keys())
    urls_vistas = set()
    todas_as_vagas = []
    total_combinacoes = 0
    total_duplicadas = 0
    total_ja_no_firebase = 0
    total_fora_escopo = 0
    inicio = time.time()

    for palavra in parametros['palavras_chave']:
        termos_keyword = _termos_da_keyword(palavra)
        for modalidade in parametros['modalidades']:
            total_combinacoes += 1

            logger.info(f"Buscando '{palavra}' — '{modalidade}'...")

            vagas_encontradas = scraper.buscar_vagas(palavra, modalidade, parametros['limite_busca'])

            vagas_novas, duplicadas, ja_firebase = filtrar_duplicadas(
                vagas_encontradas, urls_vistas, ids_firebase
            )
            total_duplicadas += duplicadas
            total_ja_no_firebase += ja_firebase

            vagas_novas, n_fora_escopo = _filtrar_por_relevancia(vagas_novas, termos_keyword)
            total_fora_escopo += n_fora_escopo
            if n_fora_escopo:
                logger.warning(f"  🚫 {n_fora_escopo} vaga(s) fora do escopo rejeitada(s).")

            # Grava só as vagas desta combinação (merge). Se o job for
            # cancelado, a rota fica com as vagas de ontem + as de hoje,
            # nunca menor do que estava.
            if vagas_novas:
                logger.info(f"  ✅ {len(vagas_novas)} vagas únicas adicionadas.")
                todas_as_vagas.extend(vagas_novas)
                enviar_para_firebase(vagas_novas, rota, ids_firebase)
            elif duplicadas > 0 or ja_firebase > 0:
                logger.info(f"  ⏭️ {duplicadas} duplicadas, {ja_firebase} já no Firebase.")
            else:
                logger.info(f"  ⚠️ Nenhuma vaga encontrada.")

    duracao = time.time() - inicio

    return {
        'vagas': todas_as_vagas,
        'total_combinacoes': total_combinacoes,
        'total_duplicadas': total_duplicadas,
        'total_ja_no_firebase': total_ja_no_firebase,
        'total_fora_escopo': total_fora_escopo,
        'duracao_segundos': duracao,
    }


# ============================================================
# FINALIZAÇÃO — métricas + snapshot final completo
# ============================================================
def coleta_saudavel(total_vagas: int, total_snapshot: int, minimo_vagas: int) -> bool:
    """A coleta só vale como completa se passar do mínimo absoluto e da fração do snapshot."""
    if total_vagas < minimo_vagas:
        logger.error(f"[SAÚDE] Coleta de {total_vagas} vagas abaixo do mínimo ({minimo_vagas}).")
        return False
    if total_vagas < total_snapshot * PROPORCAO_MINIMA_SNAPSHOT:
        logger.error(
            f"[SAÚDE] Coleta de {total_vagas} vagas é menos de "
            f"{PROPORCAO_MINIMA_SNAPSHOT:.0%} das {total_snapshot} que já estavam na rota."
        )
        return False
    return True


def finalizar_scraping(resultados: dict, rota: str, ids_existentes: set, minimo_vagas: int) -> bool:
    """
    Imprime métricas e, se a coleta foi saudável, remove as vagas expiradas.
    Retorna False quando a coleta veio quebrada (o job deve falhar).
    """
    duracao = resultados['duracao_segundos']
    total_vagas = len(resultados['vagas'])

    logger.info("-" * 60)
    logger.info(f"Orquestração finalizada!")
    logger.info(f"  • Combinações pesquisadas: {resultados['total_combinacoes']}")
    logger.info(f"  • Vagas únicas coletadas: {total_vagas}")
    logger.info(f"  • Duplicadas ignoradas (intra-scraping): {resultados['total_duplicadas']}")
    logger.info(f"  • Já existentes no Firebase: {resultados['total_ja_no_firebase']}")
    logger.info(f"  • Fora do escopo rejeitadas: {resultados.get('total_fora_escopo', 0)}")
    logger.info(f"  • Duração: {duracao / 60:.1f} minutos ({duracao:.0f}s)")

    if total_vagas > 0:
        vagas_por_segundo = total_vagas / duracao if duracao > 0 else 0
        taxa_duplicata = resultados['total_duplicadas'] / (total_vagas + resultados['total_duplicadas']) * 100 if (total_vagas + resultados['total_duplicadas']) > 0 else 0
        logger.info(f"  • Performance: {vagas_por_segundo:.1f} vagas/segundo")
        logger.info(f"  • Taxa de duplicatas: {taxa_duplicata:.1f}%")

    saudavel = coleta_saudavel(total_vagas, len(ids_existentes), minimo_vagas)
    if saudavel:
        ids_coletados = {vaga['id'] for vaga in resultados['vagas']}
        remover_expiradas(ids_coletados, ids_existentes, rota)
    else:
        logger.warning(f"Coleta quebrada: vagas expiradas mantidas em '{rota}' até a próxima coleta completa.")

    logger.info("=" * 60)
    return saudavel


# ============================================================
# ENTRY POINT — chamado pelos mains específicos
# ============================================================
def executar(scraper: ScraperProtocol, plataforma: str, categorias: dict):
    """
    Executa o ciclo completo de scraping para todas as categorias.

    Args:
        scraper: instância do scraper (GupyScraper, LinkedinScraper, etc)
        plataforma: nome da plataforma (para logs)
        categorias: dict com as categorias a processar, formato:
            {
                "dev": {"queries": "queries/tecnologia_gupy.json", "rota": "/vagas/dev/gupy"},
                "adv": {"queries": "queries/advogados_gupy.json",  "rota": "/vagas/adv/gupy"},
            }
    """
    configurar_logging()

    logger.info("=" * 60)
    logger.info(f"INICIANDO MYORBITA SCRAPER — PLATAFORMA: {plataforma.upper()}")
    logger.info("=" * 60)

    inicializar_firebase()
    inicio_total = time.time()
    categorias_quebradas = []

    for nome_categoria, categoria in categorias.items():
        logger.info(f"\n{'=' * 60}")
        logger.info(f"CATEGORIA: {nome_categoria.upper()}")
        logger.info(f"{'=' * 60}")

        config = carregar_configuracoes(categoria['queries'])
        if not config:
            categorias_quebradas.append(nome_categoria)
            continue

        parametros = extrair_parametros(config)
        exibir_info_configuracoes(parametros, plataforma)

        snapshot_firebase = carregar_snapshot_firebase(categoria['rota'])

        resultados = executar_buscas(scraper, parametros, snapshot_firebase, categoria['rota'])
        saudavel = finalizar_scraping(
            resultados, categoria['rota'], set(snapshot_firebase.keys()), parametros['minimo_vagas']
        )
        if not saudavel:
            categorias_quebradas.append(nome_categoria)

    duracao_total = time.time() - inicio_total
    logger.info(f"\n{'=' * 60}")
    logger.info(f"EXECUÇÃO COMPLETA — {plataforma.upper()}")
    logger.info(f"  Duração total: {duracao_total / 60:.1f} minutos ({duracao_total:.0f}s)")
    logger.info(f"{'=' * 60}")

    # Falha o job para o GitHub Actions ficar vermelho: antes, 0 vagas
    # coletadas terminava como sucesso e ninguém percebia a quebra.
    if categorias_quebradas:
        logger.error(f"Categorias com coleta quebrada: {', '.join(categorias_quebradas)}")
        sys.exit(1)