"""
Adapter: persistencia en Weaviate con embeddings para búsqueda semántica.

Requiere: pip install weaviate-client

Configuración típica:
- WEAVIATE_URL (ej. http://localhost:8080)
- Colección "Article" con vectorizer (text2vec-openai, text2vec-transformers, etc.)
"""
from datetime import datetime
from zoneinfo import ZoneInfo

import weaviate
from weaviate.classes.query import Filter, Move
from weaviate.collections.classes.grpc import MetadataQuery

from domain.entities import Article
from domain.ports.article_repository_port import ArticleRepositoryPort
import traceback
from weaviate.classes.config import Configure, Property, DataType
from pprint import pprint
from weaviate.classes.backup import BackupLocation
import os

import types
from typing import get_origin, get_args, Any, Dict, List, Type, Union
from pydantic import BaseModel

COLLECTION = "news"

class WeaviateArticleRepository(ArticleRepositoryPort):
    def _helper_type_python_to_wv(self, t):
        """
        :param t: tipo python
        :return: typo weaviate
        """
        mapping = {
            str: DataType.TEXT,
            int: DataType.INT,
            float: DataType.NUMBER,
            datetime: DataType.DATE,
            bool: DataType.BOOL,
        }
        return mapping.get(t, "text")

    def _unwrap_optional(self, type_hint):
        """If type_hint is Optional[T] (i.e., Union[T, None]), return T.
           Otherwise return type_hint unchanged."""
        origin = get_origin(type_hint)
        if origin is Union or origin is types.UnionType:
            args = get_args(type_hint)
            non_none_args = [a for a in args if a is not type(None)]
            if len(non_none_args) == 1:
                return non_none_args[0]
        return type_hint

    def _helper_model_to_weaviate_properties(self, model: Type[BaseModel]) -> List[Property]:
        weaviate_properties = []

        for field_name, field_info in model.model_fields.items():
            # Get the raw type of the field (e.g., str, List[str], int, etc.)
            field_type = self._unwrap_optional(field_info.annotation)

            # Determine the corresponding Weaviate DataType
            if field_type is str:
                weaviate_type = DataType.TEXT
            elif field_type is int:
                weaviate_type = DataType.INT
            elif field_type is bool:
                weaviate_type = DataType.BOOL
            elif field_type is float:
                weaviate_type = DataType.NUMBER
            elif field_type is datetime:
                weaviate_type = DataType.DATE
            # Check for List[str] (Array of text)
            elif get_origin(field_type) is list and get_args(field_type)[0] is str:
                weaviate_type = DataType.TEXT_ARRAY
            # ... you can add more type mappings here ...
            else:
                # If it's a nested model, you might want to mark it as an OBJECT
                # and recursively generate its properties (a bit more complex)
                raise ValueError(f"Unsupported type {field_type} for field {field_name}")

            # Create the Weaviate Property object
            weaviate_properties.append(
                Property(name=field_name, data_type=weaviate_type)
            )

        return weaviate_properties

    def _helper_create_collection(self) -> None:
        """Crea una colección con auto-embedding"""

        # Abortar si ya existe
        if self.client.collections.exists(self.collection_name):
            # nunca deberiamos llegar aca pq "_helper_create_collection" es llamada cuando collection no existe
            print(f"error: intentando recrear colección {self.collection_name} prexistente")
            exit(1)

        # Crear la clase
        try:
            properties = self._helper_model_to_weaviate_properties(Article)
        except Exception as e:
            print(f"Error validando modelo Pydantic Articulo:\n{e}")
            exit(1)

        try:
            # Definir el schema
            self.client.collections.create(
                self.collection_name,
                description="noticias bajadas feeds rss",
                vector_config=[
                    Configure.Vectors.text2vec_transformers(
                        name="content",
                        source_properties=["content"]
                    )
                ],
                properties=properties
            )
        except Exception as e:
            print(f"Error al crear collection weaviate:\n{e}")
            print("Propiedades de la collection:")
            pprint(properties)
            self.client.close()
            exit(1)
        return

    def _helper_weaviate_connect(self):
        url = os.getenv("WEAVIATE_URL")
        if url is None:
            url = "http://localhost:8080"
            print(f"WEAVIATE_URL environment variable not found, defaulting to {url}")
        else:
            print(f"found environment WEAVIATE_URL={url}")

        # Parse the URL to extract host, port, and scheme for connect_to_custom()
        # For a standard URL like "http://weaviate:8080", this is straightforward.
        # For more complex scenarios, you might use urllib.parse.

        # For this example, assuming the URL is in the format "http://<host>:<port>"
        parts = url.split("://")
        scheme = parts[0]  # "http" or "https"
        host_port = parts[1].split(":")
        host = host_port[0]  # "weaviate"
        port = int(host_port[1]) if len(host_port) > 1 else (443 if scheme == "https" else 80)

        # Determine if the connection is secure
        is_secure = scheme == "https"

        try:
            # Use the context manager for automatic connection handling
            self.client = weaviate.connect_to_custom(
                    http_host=host,
                    http_port=port,
                    http_secure=is_secure,
                    grpc_host=host,  # gRPC host, often the same
                    grpc_port=50051,  # Standard gRPC port, adjust if needed
                    grpc_secure=is_secure,
                    headers={
                        # Add API keys here if authentication is required (e.g., for Weaviate Cloud)
                        # "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
                    },
                    skip_init_checks=True,
            )
            # Check if the connection is live
            if self.client.is_ready():
                print(f"conexion weaviate lista: {self.client.get_meta()['hostname']}")
            else:
                print(f"Error de conexión, {url=}")
                traceback.print_exc()
                exit(1)
        except Exception as e:
            print(f"Failed to connect to Weaviate, {url=} {scheme=} {host=} {is_secure=}:\n{e}")
            exit(1)

        try:
            self.client.connect()
            print(f"Connected weaviate version {weaviate.__version__}")
        except Exception as e:
            print(f"Failed client.connect(): {e}")

    def __init__(self):
        f"""
        Conectarse a la BD, a la collecion {COLLECTION} y setear "self.collection" (que recibirá queries)
        """
        self._helper_weaviate_connect()
        print("__init__: _helper_weaviate_connect() ok")

        self.collection_name = COLLECTION
        if self.client.collections.exists(self.collection_name):
            print(f"Usando collection {self.collection_name} existente")
        else:
            print(f"Creando collection {self.collection_name}")
            self._helper_create_collection()
        self.collection = self.client.collections.use(COLLECTION)

    def __del__(self):
        self.client.close()

    def add(self, article: Article) -> None:
        properties = {
            "titulo": article.titulo.lower(),
            "resumen": article.resumen,
            "pub_date": article.pub_date,
            "poll_date": article.poll_date,
            "medio": article.medio,
            "url": article.url,
            "feed_url": article.feed_url,
            "article_raw": article.article_raw,
            "periodista": article.periodista,
        }

        # Obtener la colección
        try:
            # collection = self.client.collections.poll(self.collection_name)
            result = self.collection.data.insert(properties=properties)
        except Exception as e:
            print(f"Error al agregar datos a collection weaviate '{self.collection_name}':\n{e}")
            print("Propiedades del objeto:")
            pprint(properties)
            self.client.close()
            exit(1)
        print(f"se guardo {result} - ({properties.get('medio')}){properties.get('titulo')}")
        return

    def add_batch(self, articles: list[Article]) -> None:
        for art in articles:
            self.add(art)
        return

    #         self, query: str, limit: int = 5, medio: str | None = None
    def find_similar(self, query: str|None, limit: int = 5, medio: str | None = None) -> list[Article]:
        """
        Busca artículos por conceptos con filtro opcional de fuente
        :param limit:
        ejemplos: https://docs.weaviate.io/weaviate/tutorials/query
        Busqueda similitud: nearText https://docs.weaviate.io/weaviate/api/graphql/search-operators#neartext
        Busqueda keyword: bm25 https://docs.weaviate.io/weaviate/api/graphql/search-operators#bm25
        """
        # Construir el diccionario near_text base
        if query:
            query_parms = {
                "query": query,
                # "certainty": certainty,
                "limit": limit,
            }
        else:
            query_parms = None

        # Añadir filtro si se especifica fuente
        if medio:
            filters = Filter.by_property("medio").equal(medio)
        else:
            filters = None

        # query.hybrid no soporta "move_away"
        # if avoid:
        #     # move_away=Move(force=0.45, concepts="finance"),
        #     move_away = Move(concepts=avoid, force=avoid_force)
        # else:
        #     move_away = None

        if query_parms is None:
            # busqueda unicamente por filtro: "fech_objects"
            response = self.collection.query.fetch_objects(filters=filters)
        else:
            # buqueda por proximidad y (tal vez) filtrando
            response = self.collection.query.hybrid(
                **(query_parms),
                filters=filters,
                return_metadata=MetadataQuery(score=True, explain_score=True),
            )
        art=[]
        explain=True
        # Extraer resultados
        for o in response.objects:
            art.append(Article(
                titulo = o.properties.get('titulo'),
                resumen = o.properties.get('resumen'),
                pub_date = o.properties.get('pub_date'),
                poll_date=o.properties.get('poll_date'),
                periodista=o.properties.get('periodista'),
                url = o.properties.get('url'),
                medio = o.properties.get('medio'),
                feed_url = o.properties.get('feed_url'),
                article_raw = o.properties.get('article_raw') or o.properties.get('raw'),
            ))
            if (explain):
                print(f"{o.properties.get('medio')} [{o.properties.get('titulo')}]")
                # print(f"(explain) properties={o.properties}")
                print(f"(explain) score={o.metadata.score, o.metadata.explain_score}")
        return art

    def find_keywords(
            self, keywords: list[str], medio: str | None = None, limit: int = 20
    ) -> list[Article]:
        # TODO: query Weaviate con filtro por keywords
        if self._fallback:
            return self._fallback.find_keywords(keywords, medio, limit)
        return self._simple_keyword_search(keywords, medio, limit)

    def backup(self) -> None:
        bkpid = f"backup_{datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).strftime("%Y-%m-%d.%H:%M")}"
        result = self.client.backup.create(
            backup_id=bkpid,
            backend="filesystem",
            include_collections=[self.collection_name],
            wait_for_completion=True,
            backup_location=BackupLocation.FileSystem(path="/var/lib/weaviate/backups"),
        )
        print(f"backup {bkpid}\n{result}")

    # def find_similar(self, query: str, medio: str | None = None, limit: int = 20) -> list[Article]:
    #     return self.seach_proximity(self,concepts=query, source=medio, limit=limit)
    #
    def _simple_keyword_search(
            self, keywords: list[str], medio: str | None, limit: int
    ) -> list[Article]:
        result = []
        kw_lower = [k.lower() for k in keywords]
        for a in self._articles:
            if medio and a.medio != medio:
                continue
            texto = f"{(a.titulo or '')} {(a.resumen or '')}".lower()
            if any(k in texto for k in kw_lower):
                result.append(a)
                if len(result) >= limit:
                    break
        return result
