# scrapers/linkedin_enricher.py
"""
Enriquecedor LinkedIn — preenche tipo_contrato nas vagas salvas.

Fluxo:
    1. Lê todas as vagas da rota Firebase com tipo_contrato == "Não informado"
    2. Para cada uma, acessa a página interna via _extrair_contrato_pagina_interna
    3. Atualiza apenas o campo tipo_contrato via ref.child(id).update()

Separado do scraper principal para não impactar o volume de requests
da coleta de listagem. Roda como job independente.
"""
import logging
from firebase_admin import db
from .linkedin_scraper import LinkedinScraper

logger = logging.getLogger(__name__)


class LinkedinEnricher(LinkedinScraper):
    """
    Herda LinkedinScraper para reusar session curl_cffi, warm-up,
    _extrair_contrato_pagina_interna e todas as proteções anti-detecção.
    Não implementa buscar_vagas — não é um scraper de listagem.
    """

    def enriquecer_rota(self, rota: str, limite: int = 200):
        """
        Lê vagas pendentes do Firebase e preenche tipo_contrato.

        Args:
            rota: caminho Firebase, ex: '/vagas/dev/linkedin'
            limite: máximo de vagas a enriquecer por execução (evita timeout no Actions)
        """
        self._aquecer_session()

        pendentes = self._carregar_pendentes(rota, limite)
        if not pendentes:
            logger.info(f"[ENRICHER] Nenhuma vaga pendente em '{rota}'")
            return

        logger.info(f"[ENRICHER] {len(pendentes)} vagas pendentes em '{rota}'")

        atualizadas = 0
        falhas = 0

        for i, (id_vaga, vaga) in enumerate(pendentes.items()):
            if self._circuit_breaker_aberto():
                logger.error(
                    "[ENRICHER] Circuit breaker aberto — abortando enriquecimento")
                break

            link = vaga.get('link')
            if not link:
                falhas += 1
                continue

            logger.info(
                f"[ENRICHER] [{i + 1}/{len(pendentes)}] {vaga.get('titulo', '?')} — {link}")

            tipo_contrato = self._extrair_contrato_pagina_interna(link)

            if tipo_contrato != 'Não informado':
                self._atualizar_contrato_firebase(rota, id_vaga, tipo_contrato)
                atualizadas += 1
                logger.info(f"[ENRICHER] ✅ tipo_contrato: '{tipo_contrato}'")
            else:
                falhas += 1
                logger.info(f"[ENRICHER] ⚠️ tipo_contrato não encontrado")

        logger.info(
            f"[ENRICHER] Concluído '{rota}': "
            f"{atualizadas} atualizadas, {falhas} sem contrato encontrado"
        )

    def _carregar_pendentes(self, rota: str, limite: int) -> dict:
        """Retorna dict {id: vaga} com tipo_contrato == 'Não informado', até `limite` itens."""
        try:
            ref = db.reference(rota)
            snapshot = ref.get()
            if not snapshot or not isinstance(snapshot, dict):
                return {}

            pendentes = {
                id_vaga: vaga
                for id_vaga, vaga in snapshot.items()
                if isinstance(vaga, dict) and vaga.get('tipo_contrato') == 'Não informado'
            }

            # Limita para não estourar timeout do Actions
            ids_limitados = list(pendentes.keys())[:limite]
            return {k: pendentes[k] for k in ids_limitados}

        except Exception as e:
            logger.error(
                f"[ENRICHER] Falha ao carregar pendentes de '{rota}': {e}")
            return {}

    def _atualizar_contrato_firebase(
            self,
            rota: str,
            id_vaga: str,
            tipo_contrato: str):
        """Atualiza apenas o campo tipo_contrato da vaga — não sobrescreve o resto."""
        try:
            db.reference(
                f"{rota}/{id_vaga}").update({'tipo_contrato': tipo_contrato})
        except Exception as e:
            logger.error(f"[ENRICHER] Falha ao atualizar {id_vaga}: {e}")
