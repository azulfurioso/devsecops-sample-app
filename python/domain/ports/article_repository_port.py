from abc import ABC, abstractmethod

from domain.entities import Article


class ArticleRepositoryPort(ABC):
    """Puerto para persistencia de artículos (Weaviate, memoria, etc.)."""

    @abstractmethod
    def add(self, article: Article) -> None:
        """Guarda un artículo."""
        ...

    @abstractmethod
    def add_batch(self, articles: list[Article]) -> None:
        """Guarda múltiples artículos (con embeddings para búsqueda semántica)."""
        ...

    @abstractmethod
    def find_keywords(
        self, query: list[str], limit: int = 5, medio: str | None = None
    ) -> list[Article]:
        """Busca por palabras clave en título/descripción."""
        ...

    @abstractmethod
    def find_similar(
        self, query: str|None, limit: int = 5, medio: str | None = None
    ) -> list[Article]:
        """Busca por similitud semántica (embeddings)."""
        ...
