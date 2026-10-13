# 📌 Wiring: acá se mezcla capas (framework, adapters, use cases).

import argparse
import yaml
from sys import exit

from adapters.cli.console_show import CliController
from adapters.feeds.article_read_rss import GetArticleRss
# from adapters.persistence.memory_repo import MemoryArticleRepository # descomentar para usar memory repo
from adapters.persistence.article_repository_weaviate import WeaviateArticleRepository
from domain.ports.article_read_port import GetArticle
from use_cases.poll_feed import PollFeeds
from use_cases.search_news import SearchNews
from domain.entities import Feed, Article

def _parse_feeds_from_yaml(path: str) -> list[Feed]:
    """Parsea el YAML y devuelve todos los feeds habilitados."""
    try:
        with open(path, encoding='utf-8') as f:
            datos = yaml.safe_load(f)
    except Exception as e:
        print(f"Error leyendo feed file '{path}': {e}")
        exit(1)

    sources: list[Feed] = []
    for medio in datos.get('medios'):
        if medio.get('activo') is False:
            continue
        nombre = medio['nombre']
        for feed in medio.get('feeds'):
            if feed.get('poll') is False:
                continue
            sources.append(Feed(medio=nombre, url=feed['url']))
    return sources

def load_feeds(path: str) -> list[Feed]:
    """
    Devuelve todos los feeds habilitados (activo: True, poll: True).
    En cada poll se obtienen todos los artículos; la dedup al persistir evita duplicados.
    """
    return _parse_feeds_from_yaml(path)

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--feeds", default="medios.yaml")
    parser.add_argument("--medio")
    parser.add_argument("--show_summary", action="store_true", help="Muestra el resumen en modo no interactivo")

    # Crear grupo mutuamente excluyente
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--keywords", nargs="*", help="Búsqueda por keywords")
    group.add_argument("--semantic", nargs="*", help="Búsqueda por similitud semántica")
    group.add_argument("--backup", help="backup vector DB")

    return parser


def run_interactive_menu(feeds: list[Feed], repository) -> None:
    """CLI interactivo para poll_persist y búsqueda."""
    rss_reader = GetArticleRss()
    poll_uc = PollFeeds(rss_reader)
    search_uc = SearchNews()
    controller = CliController()

    while True:
        print("\n=== RSS Reader ===")
        print("1) Poll & persist feeds")
        print("2) Buscar noticias")
        print("b) Tomar Backup")
        print("q) Salir")
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            print("\nLeyendo feeds y persistiendo artículos (solo nuevos)...")
            poll_uc.poll_persist(feeds, repository)

        elif opcion == "2":
            print("\n--- Búsqueda de noticias ---")
            medio = input("Medio (enter para cualquiera): ").strip() or None

            print("Tipo de búsqueda:")
            print("  1) Keywords")
            print("  2) Semántica")
            tipo = input("Elige [1/2]: ").strip()

            keywords = None
            semantic_query = None
            if tipo == "1":
                txt = input("Texto de keywords: ").strip()
                keywords = txt or None
            elif tipo == "2":
                txt = input("Texto para búsqueda semántica: ").strip()
                semantic_query = txt or None
            else:
                print("Opción de búsqueda no válida.")
                continue

            limit_str = input("Límite de resultados [5]: ").strip()
            try:
                limit = int(limit_str) if limit_str else 5
            except ValueError:
                print("Límite inválido, usando 5 por defecto.")
                limit = 5

            try:
                results = search_uc.retrieve(
                    repository=repository,
                    medio=medio,
                    keywords=keywords,
                    semantic_query=semantic_query,
                    limit=limit,
                )
            except ValueError as e:
                print(f"Error en la búsqueda: {e}")
                continue

            controller.show(results)

        elif opcion == "b":
            print("Efectuando Backup de Weaviate")
            repository.backup()

        elif opcion == "q":
            print("Saliendo...")
            break

        else:
            print("Opción no válida. Intenta de nuevo.")


def main():
    args = build_parser().parse_args()
    feeds = load_feeds(args.feeds)

    # Wiring: persistencia
    repository = WeaviateArticleRepository()  # donde se persistirán los artículos

    # Si se pasan parámetros de búsqueda, mantenemos el modo "una sola ejecución" actual.
    tiene_parametros_busqueda = any([args.medio, args.keywords, args.semantic])
    if tiene_parametros_busqueda:
        query_semantic = query_keywords = None
        if args.semantic:
            query_semantic = args.semantic[0]
        if args.keywords:
            query_keywords = args.keywords[0]

        rss_reader = GetArticleRss()
        poll_uc = PollFeeds(rss_reader)
        poll_uc.poll_persist(feeds, repository)

        results = SearchNews().retrieve(
            repository=repository,
            medio=args.medio,
            keywords=query_keywords,
            semantic_query=query_semantic,
            limit=5,
        )

        controller = CliController()
        controller.show(results, summary=args.show_summary)
    else:
        # Sin accion especifica => leer feeds
        #run_interactive_menu(feeds, repository)
        print("\nLeyendo feeds y persistiendo artículos (solo nuevos)...")
        rss_reader = GetArticleRss()
        poll_uc = PollFeeds(rss_reader)
        poll_uc.poll_persist(feeds, repository)


if __name__ == "__main__":
    main()
