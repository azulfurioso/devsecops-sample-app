i✔ lógica testeable
✔ RSS reemplazable
✔ CLI → Web sin tocar core
✔ SQLite/YAML mañana sin reescribir nada
✔ arquitectura explicable en 30 segundos


main:
    repository = WeaviateArticleRepository()    # donde se persistiran

    rss_reader = GetArticleRss()                # extiende "GetArticle", immplementa read(): Feed -> List[Articles]
    poll_uc = GetArticles(rss_reader)           # el constructor recibe una clase "GetArticle" (con un metodo "read")
    articles = poll_uc.get(feeds)               # usa metodo "get" para obtener los articulos

                                                # implementa get(): list[FeedSource] -> list[Articles]
    search_uc = SearchNews(repository)
    controller = CliController()

domain/ports/article_read_port.py:              # declara ABS "GetArticle" con metodo read(): Feed -> list[Articles]
adapters/feeds/article_read_rss.py:             # implementa "GetArticleRss" donde "read()" hace fetch https

use_cases/poll_feed.py:                         # declara "PoolFeeds" con metodo poll(): list[Feed] -> list[Articles]


main:
    rss_reader = GetArticleRss()                # Creo lector de articulos rss
    poll_uc = PollFeeds(rss_reader)             # Preparo lectura de todos los feed
    articles = poll_uc.poll(feeds)              # Leo todos todos los feeds

    repository = WeaviateArticleRepository()    # donde se persistiran
    search_uc = SearchNews(repository)
    controller = CliController()

