from abc import ABC, abstractmethod

from domain.entities import Article, Feed


class GetArticle(ABC):
    """Puerto para leer feeds RSS desde una URL."""

    @abstractmethod
    def read(self, feed: Feed) -> [Article]:
        """Obtiene los artículos desde la URL del feed."""