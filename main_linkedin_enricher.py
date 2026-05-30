from scrapers.linkedin_enricher import LinkedinEnricher
from scraper_runner import configurar_logging, inicializar_firebase
import logging

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

    for rota in ROTAS:
        enricher.enriquecer_rota(rota, limite=LIMITE_POR_ROTA)
