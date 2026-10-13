from domain.entities import Article, Feed
from domain.ports.article_read_port import GetArticle

class PollFeeds:
    """Caso de uso: leer feeds RSS y obtener artículos. No persiste."""

    def __init__(self, rss_reader: GetArticle):
        self.rss_reader = rss_reader

    def poll(self, feeds: [Feed]) -> [Article]:
        """Obtiene todos los artículos de los feeds. La persistencia con dedup es responsabilidad del framework."""
        all_articles = []
        for f in feeds:
            feed = Feed(url=f.url, medio=f.medio)
            articles = self.rss_reader.read(feed)
            all_articles.extend(articles)
        return all_articles


