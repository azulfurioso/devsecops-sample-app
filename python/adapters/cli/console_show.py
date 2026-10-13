from datetime import datetime

from domain.entities import Article


class CliController:
    def show(self, articles: [Article], summary: bool = True):
        for art in articles:
            fecha=art.pub_date.strftime('%d/%b %H:%M') if isinstance(art.pub_date, datetime) else "N/A"
            print(f"{art.medio} [{art.titulo}] - {fecha}")
            if summary and art.resumen:
                print(art.resumen)
                print("-" * 40)
