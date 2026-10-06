"""
main_linkedin_adv.py — Entry point do scraper LinkedIn para categoria ADV.

Rodado por: .github/workflows/linkedin-adv.yml
Consome:    queries/advogados_linkedin.json
Publica em: /vagas/adv/linkedin (Firebase Realtime DB)

A orquestração propriamente dita vive em scraper_runner.py
(DRY — mesmo código compartilhado com main_gupy.py e main_linkedin_dev.py).

Por que split DEV/ADV?
Separar em dois workflows com crons distintos isola falhas: se DEV quebrar,
ADV roda independente. (Antes de 05/10/2026 a busca fazia uma requisição
por modalidade e página, e DEV + ADV não cabiam nas 6h do GitHub Actions.)
"""
from scrapers.linkedin_scraper import LinkedinScraper
from scraper_runner import executar

CATEGORIAS = {
    "adv": {
        "queries": "queries/advogados_linkedin.json",
        "rota":    "/vagas/adv/linkedin",
    },
}

if __name__ == "__main__":
    executar(
        scraper=LinkedinScraper(),
        plataforma="linkedin-adv",
        categorias=CATEGORIAS,
    )