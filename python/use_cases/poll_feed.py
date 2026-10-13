from domain.entities import Article, Feed
from domain.ports.article_read_port import GetArticle
from domain.ports.article_repository_port import ArticleRepositoryPort
from pathlib import Path
import json
import os

_last_poll_dir = os.getenv("LAST_POLL_DIR")
if _last_poll_dir is None:
    print(f"LAST_POLL_DIR environment variable not found")
    exit(1)
LAST_POLL_DIR = Path(_last_poll_dir)
PERSISTED_LINKS_FILE = LAST_POLL_DIR / "persisted_links.json"
print(f"Cache of processed articles {PERSISTED_LINKS_FILE=}")

class PollFeeds:
    """Caso de uso: leer feeds RSS y obtener artículos. No persiste."""

    def __init__(self, rss_reader: GetArticle):
        self.rss_reader = rss_reader
        self.polled_articles = None

    def poll(self, feeds: [Feed]) -> [Article]:
        """Obtiene todos los artículos de los feeds. La persistencia con dedup es responsabilidad del framework."""
        all_articles = []
        for f in feeds:
            articles = self.rss_reader.read(f)
            all_articles.extend(articles)
        self.polled_articles = all_articles
        return all_articles

    def persist(self, articles: [Article], repository: ArticleRepositoryPort):
        # Persistir solo los nuevos (evitar duplicados por link)
        persisted = self._load_persisted_links()
        nuevos = [a for a in self.polled_articles if a.url not in persisted]
        if nuevos:
            repository.add_batch(nuevos)
            persisted.update(a.url for a in nuevos)
            self._save_persisted_links(persisted)
        else:
            print(f"No hay articulos nuevos: los {len(self.polled_articles)} articulos puleados ya estan persistidos")

    def poll_persist(self, feeds: [Feed], repository: ArticleRepositoryPort):
        articles = self.poll(feeds)      # Leo todos todos los feeds
        self.persist(articles,repository)

    def _save_persisted_links(self,links: set[str]) -> None:
        """G
        uarda los links persistidos. Se llama tras cada poll."""
        LAST_POLL_DIR.mkdir(exist_ok=True)
        with open(PERSISTED_LINKS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'links': sorted(links)}, f, indent=2)

    def _load_persisted_links(self) -> set[str]:
        """Carga el conjunto de links de artículos ya persistidos."""
        if not PERSISTED_LINKS_FILE.exists():
            return set()
        try:
            with open(PERSISTED_LINKS_FILE, encoding='utf-8') as f:
                data = json.load(f)
            return set(data.get('links'))
        except (json.JSONDecodeError, OSError):
            return set()




