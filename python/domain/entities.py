# Entidades de dominio: existen independientemente de YAML, RSS, Weaviate, etc.

from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

@dataclass
class Medio:
    nombre: str
    pais: str
    idioma: str
    orientacion_politica: str


@dataclass
class Feed:
    url: str
    medio: str
    last_poll: datetime | None = None
    poll_freq: int = 4 * 60 # in minutes
    active: bool = True     # inhibir polling automatico si False


class Article(BaseModel):
    model_config = ConfigDict(extra="forbid")
    titulo: str = Field(
        description="Título del artículo",
        json_schema_extra={
            "index_filterable": False,
            "index_searchable": True,
            "vectorize": True,
        }
    )


    resumen: str | None = Field(
        default=None,
        description="Resumen del artículo",
        json_schema_extra={
            "index_filterable": False,
            "index_searchable": True,
            "vectorize": True,
        }
    )

    # campos sin vectorizar (filtrables por "where", no por proximidad)
    pub_date: datetime | None = Field(
        default=None,
        description="Fecha de publicación",
        json_schema_extra={
            "index_filterable": False,
            "index_searchable": True,
            "vectorize": False,
        }
    )

    poll_date: datetime | None = Field(
        default=None,
        description="Fecha de polling / extraccion",
        json_schema_extra={
            "index_filterable": False,
            "index_searchable": True,
            "vectorize": False,
        }
    )

    periodista: str | None = Field(
        default=None,
        description="Autor del artículo",
        json_schema_extra={
            "index_filterable": False,
            "index_searchable": True,
            "vectorize": False,
        }
    )

    url: str = Field(
        description="URL  del artículo",
        json_schema_extra={
            "index_filterable": False,
            "index_searchable": True,
            "vectorize": False,
        }
    )

    medio: str = Field(
        description="medio que publico el artículo",
        json_schema_extra={
            "index_filterable": False,
            "index_searchable": True,
            "vectorize": False,
        }
    )

    feed_url: str = Field(
        description="URL del feed donde estaba el artículo",
        json_schema_extra={
            "index_filterable": False,
            "index_searchable": True,
            "vectorize": False,
        }
    )

    article_raw: str = Field(
        description="Contenido raw del articulo",
        json_schema_extra={
            "index_filterable": False,
            "index_searchable": True,
            "vectorize": False,
        }
    )