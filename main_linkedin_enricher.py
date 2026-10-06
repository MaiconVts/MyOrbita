from scrapers.linkedin_enricher import LinkedinEnricher
from scraper_runner import configurar_logging, inicializar_firebase
import logging
import sys

logger = logging.getLogger(__name__)

ROTAS = [
    '/vagas/dev/linkedin',
    '/vagas/adv/linkedin',
]

LIMITE_POR_ROTA = 200

if __name__ == '__main__':
    configurar_logging()
    inicializar_firebase()

    enricher = LinkedinEnricher()

    rotas_ilegiveis = [
        rota for rota in ROTAS
        if enricher.enriquecer_rota(rota, limite=LIMITE_POR_ROTA) is None
    ]

    if rotas_ilegiveis:
        logger.error(f"[ENRICHER] Rotas que não puderam ser lidas: {rotas_ilegiveis}")
        sys.exit(1)
