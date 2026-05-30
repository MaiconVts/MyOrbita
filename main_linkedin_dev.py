"""
main_linkedin_dev.py — Entry point do scraper LinkedIn para categoria DEV.

Rodado por: .github/workflows/linkedin-dev.yml
Consome:    queries/tecnologia_linkedin.json
Publica em: /vagas/dev/linkedin (Firebase Realtime DB)
"""
from scrapers.linkedin_scraper import LinkedinScraper
from scraper_runner import executar

if __name__ == '__main__':
    scraper = LinkedinScraper()
    executar(
        scraper=scraper,
        plataforma='linkedin-dev',
        categorias={
            'dev': {
                'queries': 'queries/tecnologia_linkedin.json',
                'rota': '/vagas/dev/linkedin',
            }
        }
    )
