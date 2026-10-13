from domain.entities import Article
from domain.ports.article_repository_port import ArticleRepositoryPort


class MemoryArticleRepository(ArticleRepositoryPort):
    """
    Adapter: persistencia en memoria (guarda todos los articulos en "self._articles"
    Sin embeddings, búsqueda por keywords simple ("find_similar" es sinonimo de "find_by_keywords").
     """

    def __init__(self):
        self._articles: list[Article] = []

    def add(self, article: Article) -> None:
        self._articles.append(article)

    def add_batch(self, articles: list[Article]) -> None:
        self._articles.extend(articles)

    def find_keywords(self, keywords: list[str], medio: str | None = None, limit: int = 20) -> list[Article]:
        result = []
        keywords_lower = [k.lower() for k in keywords]
        for a in self._articles:
            if medio and a.medio.lower() != medio.lower():
                continue # si se indico 'medio', limitar a ése
            texto = f"{(a.titulo or '')} {(a.resumen or '')}".lower()
            if any(k in texto for k in keywords_lower):
                result.append(a)
                if len(result) >= limit:
                    break
        return result

    def find_similar(self, query: str, limit: str | None = 5, medio: int = None) -> list[Article]:
        # En memoria: simular con búsqueda por keywords del query
        return self.find_keywords(keywords=query.split(), medio=medio, limit=limit)
