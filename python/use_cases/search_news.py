from sympy.polys.polyconfig import query

from domain.entities import Article
from domain.ports.article_repository_port import ArticleRepositoryPort


class SearchNews:
    """Caso de uso: buscar noticias por keywords o por similitud semántica."""

    def __init__(self):
        pass

    def retrieve(
        self,
        repository: ArticleRepositoryPort,
        medio: str | None = None,   # puede ser "str" o "None", por defecto es "None"
        keywords: list[str] | None = None,
        semantic_query: str | None = None,
        limit: int = 20,
    ) -> list[Article]:
        print(f"keywords: '{keywords}'")
        print(f"semantic_query: '{semantic_query}'")
        print(f"medio: '{medio}'")

        if not any((medio, keywords, semantic_query)):
            raise ValueError("Debe indicar medio, keywords o búsqueda semántica")

        if keywords and semantic_query:
            raise ValueError("keywords y busqueda semantica son excluyentes")

        query = None
        if semantic_query:
            query = semantic_query
        elif keywords:
            query = keywords
        return repository.find_similar(query=query, limit=limit, medio=medio)
