"""
DTOs: objetos para transferir datos entre capas.
El core los usa pero no sabe de YAML, HTTP, CLI.
"""

from dataclasses import dataclass

@dataclass
class MedioSource:
    """Entrada de medio desde YAML (opcional, con defaults)."""
    nombre: str
    pais: str = ""
    idioma: str = "es"
    orientacion_politica: str = ""
