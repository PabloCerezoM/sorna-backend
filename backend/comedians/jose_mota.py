from backend.database.enums.comedians import ComedianStrEnum
from .base import BaseComedian


class JoseMota(BaseComedian):
    name = ComedianStrEnum.JOSE_MOTA
    name_comedian = "José Mota"

    @staticmethod
    def get_context() -> str:
        return """
        José Mota es un conocido humorista y actor español, famoso por su estilo de comedia basado en la observación y el absurdo.
        Su humor se caracteriza por la creación de personajes entrañables y situaciones cómicas que reflejan la vida cotidiana en España.
        A menudo utiliza el juego de palabras y la sátira social en sus sketches, lo que le ha valido un gran reconocimiento y popularidad.
        Mota ha trabajado en televisión, cine y teatro, y es conocido por su capacidad para conectar con el público a través de su humor inteligente y accesible.
        Su estilo es una mezcla de comedia física, diálogos ingeniosos y una profunda comprensión de la cultura española.
        """