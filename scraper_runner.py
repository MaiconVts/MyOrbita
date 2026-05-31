"""
scraper_runner.py — Orquestração compartilhada entre todas as plataformas.

Responsabilidade Única: coordenar o fluxo de execução de um scraper qualquer.
- Configura logging UTF-8 (Windows + Linux)
- Inicializa Firebase
- Carrega queries da categoria (dev/adv)
- Executa buscas com deduplicação 3 níveis
- Checkpoint Firebase a cada 10 keywords + envio final completo
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


def inicializar_firebase():
    """Inicializa Firebase uma única vez (idempotente)."""
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_KEY_PATH)
        firebase_admin.initialize_app(cred, {
            'databaseURL': FIREBASE_DB_URL
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


def enviar_para_firebase(lista_vagas: list, rota: str):
    """
    Upload da lista de vagas para o Firebase via ref.set().
    ref.set() substitui todos os dados na rota — intencional,
    sempre queremos a versão mais atualizada sem acumular lixo.
    Vagas expiradas somem automaticamente a cada execução completa.
    """
    try:
        ref = db.reference(rota)
        vagas_dict = {vaga['id']: vaga for vaga in lista_vagas}
        ref.set(vagas_dict)
        logger.info(f"[FIREBASE]: {len(lista_vagas)} vagas enviadas para '{rota}' com sucesso.")
    except Exception as e:
        logger.error(f"[FIREBASE ERRO]: Falha ao enviar dados. Erro: {str(e)}")


# ============================================================
# CONFIGURAÇÕES DE QUERIES
# ============================================================
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
    }


def exibir_info_configuracoes(parametros: dict, plataforma: str):
    """Log das configurações carregadas."""
    total_combinacoes = len(parametros['palavras_chave']) * len(parametros['modalidades'])
    logger.info(f"Configurações: {len(parametros['palavras_chave'])} palavras-chave × "
                f"{len(parametros['modalidades'])} modalidades = {total_combinacoes} combinações")
    logger.info(f"Limite por busca: {parametros['limite_busca']} vagas (com paginação automática)")
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
    Loop de buscas: itera palavras × modalidades, aplica dedup,
    faz checkpoint no Firebase a cada 10 keywords e retorna agregado.

    Checkpoint via ref.set() a cada 10 keywords garante que um timeout
    no GitHub Actions não perde mais de ~10 keywords de progresso.
    O ref.set() final em finalizar_scraping entrega o snapshot completo.
    """
    ids_firebase = set(snapshot_firebase.keys())
    urls_vistas = set()
    todas_as_vagas = []
    total_combinacoes = 0
    total_duplicadas = 0
    total_ja_no_firebase = 0
    total_fora_escopo = 0
    inicio = time.time()
    keywords_desde_checkpoint = 0

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

            # Preserva tipo_contrato já enriquecido pelo enricher.
            # O ref.set() do scraper sobrescreveria com "Não informado" sem este passo.
            for vaga in vagas_novas:
                existente = snapshot_firebase.get(vaga['id'])
                if existente:
                    tipo_existente = existente.get('tipo_contrato', 'Não informado')
                    if tipo_existente not in ('Não informado', '', None):
                        vaga['tipo_contrato'] = tipo_existente

            if vagas_novas:
                logger.info(f"  ✅ {len(vagas_novas)} vagas únicas adicionadas.")
                todas_as_vagas.extend(vagas_novas)
                logger.info(f"  💾 Snapshot: {len(todas_as_vagas)} vagas salvas no Firebase...")
                enviar_para_firebase(todas_as_vagas, rota)
            elif duplicadas > 0 or ja_firebase > 0:
                logger.info(f"  ⏭️ {duplicadas} duplicadas, {ja_firebase} já no Firebase.")
            else:
                logger.info(f"  ⚠️ Nenhuma vaga encontrada.")

        # Checkpoint a cada 10 keywords (loop externo — por palavra, não por combinação)
        keywords_desde_checkpoint += 1
        if keywords_desde_checkpoint >= 10:
            logger.info(f"  💾 Checkpoint: {len(todas_as_vagas)} vagas salvas até agora...")
            enviar_para_firebase(todas_as_vagas, rota)
            keywords_desde_checkpoint = 0

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
def finalizar_scraping(resultados: dict, rota: str):
    """Imprime métricas da categoria e envia snapshot final para o Firebase."""
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
        enviar_para_firebase(resultados['vagas'], rota)
    else:
        logger.warning("Nenhuma vaga nova encontrada. Firebase não atualizado.")

    logger.info("=" * 60)


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

    for nome_categoria, categoria in categorias.items():
        logger.info(f"\n{'=' * 60}")
        logger.info(f"CATEGORIA: {nome_categoria.upper()}")
        logger.info(f"{'=' * 60}")

        config = carregar_configuracoes(categoria['queries'])
        if not config:
            continue

        parametros = extrair_parametros(config)
        exibir_info_configuracoes(parametros, plataforma)

        snapshot_firebase = carregar_snapshot_firebase(categoria['rota'])

        resultados = executar_buscas(scraper, parametros, snapshot_firebase, categoria['rota'])
        finalizar_scraping(resultados, categoria['rota'])

    duracao_total = time.time() - inicio_total
    logger.info(f"\n{'=' * 60}")
    logger.info(f"EXECUÇÃO COMPLETA — {plataforma.upper()}")
    logger.info(f"  Duração total: {duracao_total / 60:.1f} minutos ({duracao_total:.0f}s)")
    logger.info(f"{'=' * 60}")