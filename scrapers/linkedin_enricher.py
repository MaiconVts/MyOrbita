# scrapers/linkedin_enricher.py
"""
Enriquecedor LinkedIn — preenche tipo_contrato nas vagas salvas.

Fluxo:
    1. Lê a rota Firebase e escolhe as vagas com tipo_contrato == "Não informado"
       que não foram verificadas nos últimos DIAS_ATE_REVERIFICAR dias
       (nunca verificadas primeiro, depois as verificadas há mais tempo)
    2. Para cada uma, acessa a página interna via _extrair_contrato_pagina_interna
    3. Contrato encontrado: atualiza só tipo_contrato.
       Página sem contrato: marca contrato_verificado_em, para a vaga sair
       da fila até a janela de reverificação passar.
       Falha de requisição: não grava nada; a vaga volta na próxima execução.

Separado do scraper principal para não impactar o volume de requests
da coleta de listagem. Roda como job independente.
"""
import logging
from datetime import UTC, datetime, timedelta

from firebase_admin import db

from .linkedin_scraper import LinkedinScraper

logger = logging.getLogger(__name__)

CONTRATO_PENDENTE = 'Não informado'
DIAS_ATE_REVERIFICAR = 7


def _ler_data_verificacao(valor) -> datetime | None:
    """Converte contrato_verificado_em (ISO 8601) em datetime UTC; inválido vira None."""
    if not isinstance(valor, str) or not valor:
        return None
    try:
        data = datetime.fromisoformat(valor)
    except ValueError:
        return None
    if data.tzinfo is None:
        data = data.replace(tzinfo=UTC)
    return data


def selecionar_pendentes(snapshot, limite: int, agora: datetime) -> dict:
    """
    Escolhe até `limite` vagas para enriquecer a partir do snapshot da rota.

    Entram vagas com contrato pendente e link. Ficam de fora as verificadas
    há menos de DIAS_ATE_REVERIFICAR dias. Data de verificação inválida conta
    como nunca verificada. Ordem: nunca verificadas (na ordem do snapshot),
    depois as verificadas há mais tempo.
    """
    if not isinstance(snapshot, dict):
        return {}

    corte = agora - timedelta(days=DIAS_ATE_REVERIFICAR)
    nunca_verificadas = []
    reabertas = []

    for id_vaga, vaga in snapshot.items():
        if not isinstance(vaga, dict):
            continue
        if vaga.get('tipo_contrato') != CONTRATO_PENDENTE or not vaga.get('link'):
            continue

        verificada_em = _ler_data_verificacao(vaga.get('contrato_verificado_em'))
        if verificada_em is None:
            nunca_verificadas.append((id_vaga, vaga))
        elif verificada_em <= corte:
            reabertas.append((verificada_em, id_vaga, vaga))

    reabertas.sort(key=lambda item: item[0])
    ordenadas = nunca_verificadas + [(id_vaga, vaga) for _, id_vaga, vaga in reabertas]
    return dict(ordenadas[:limite])


class LinkedinEnricher(LinkedinScraper):
    """
    Herda LinkedinScraper para reusar session curl_cffi, warm-up,
    _extrair_contrato_pagina_interna e todas as proteções anti-detecção.
    Não implementa buscar_vagas — não é um scraper de listagem.
    """

    def enriquecer_rota(self, rota: str, limite: int = 200) -> dict | None:
        """
        Lê vagas pendentes do Firebase e preenche tipo_contrato.

        Args:
            rota: caminho Firebase, ex: '/vagas/dev/linkedin'
            limite: máximo de vagas a enriquecer por execução (evita timeout no Actions)

        Returns:
            Contagens da execução, ou None se a rota não pôde ser lida.
        """
        self._aquecer_session()

        pendentes = self._carregar_pendentes(rota, limite)
        if pendentes is None:
            return None

        resumo = {'atualizadas': 0, 'sem_contrato': 0, 'falhas_requisicao': 0, 'falhas_gravacao': 0}
        if not pendentes:
            logger.info(f"[ENRICHER] Nenhuma vaga pendente em '{rota}'")
            return resumo

        logger.info(f"[ENRICHER] {len(pendentes)} vagas pendentes em '{rota}'")

        for i, (id_vaga, vaga) in enumerate(pendentes.items()):
            if self._circuit_breaker_aberto():
                logger.error(
                    "[ENRICHER] Circuit breaker aberto — abortando enriquecimento")
                break

            link = vaga['link']
            logger.info(
                f"[ENRICHER] [{i + 1}/{len(pendentes)}] {vaga.get('titulo', '?')} — {link}")

            tipo_contrato = self._extrair_contrato_pagina_interna(link)

            if tipo_contrato is None:
                resumo['falhas_requisicao'] += 1
                logger.warning("[ENRICHER] Página interna não carregou; tenta de novo na próxima execução")
                continue

            if tipo_contrato == CONTRATO_PENDENTE:
                campos = {'contrato_verificado_em': datetime.now(UTC).isoformat(timespec='seconds')}
                contagem = 'sem_contrato'
            else:
                campos = {'tipo_contrato': tipo_contrato}
                contagem = 'atualizadas'

            if not self._atualizar_vaga(rota, id_vaga, campos):
                resumo['falhas_gravacao'] += 1
                continue

            resumo[contagem] += 1
            if contagem == 'atualizadas':
                logger.info(f"[ENRICHER] ✅ tipo_contrato: '{tipo_contrato}'")
            else:
                logger.info("[ENRICHER] ⚠️ tipo_contrato não encontrado")

        logger.info(
            f"[ENRICHER] Concluído '{rota}': {resumo['atualizadas']} atualizadas, "
            f"{resumo['sem_contrato']} sem contrato na página, "
            f"{resumo['falhas_requisicao']} falhas de requisição, "
            f"{resumo['falhas_gravacao']} falhas de gravação"
        )
        return resumo

    def _carregar_pendentes(self, rota: str, limite: int) -> dict | None:
        """Lê a rota e devolve {id: vaga} escolhidas por selecionar_pendentes; None se a leitura falhar."""
        try:
            snapshot = db.reference(rota).get()
        except Exception as e:
            logger.error(
                f"[ENRICHER] Falha ao carregar pendentes de '{rota}': {e}")
            return None
        return selecionar_pendentes(snapshot, limite, datetime.now(UTC))

    def _atualizar_vaga(self, rota: str, id_vaga: str, campos: dict) -> bool:
        """Atualiza só os campos informados da vaga — não sobrescreve o resto."""
        try:
            db.reference(f"{rota}/{id_vaga}").update(campos)
        except Exception as e:
            logger.error(f"[ENRICHER] Falha ao atualizar {id_vaga}: {e}")
            return False
        return True
