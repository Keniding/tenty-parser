from typing import Any

import toon_format


class TOONTransformer:
    """
    Transforma estructuras a formato TOON (Token-Oriented Object Notation)

    Delega la codificación a la librería toon-format (implementación de
    referencia del spec: https://github.com/toon-format/spec), en vez de
    reimplementar el formato a mano.
    """

    @staticmethod
    def to_toon(data: Any, indent: int = 2) -> str:
        """Convierte datos a formato TOON"""
        return toon_format.encode(data, {"indent": indent})
