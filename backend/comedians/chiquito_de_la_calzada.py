from backend.database.enums.comedians import ComedianStrEnum
from .base import BaseComedian


class ChiquitoDeLaCalzada(BaseComedian):
    name = ComedianStrEnum.CHIQUITO_DE_LA_CALZADA

    @staticmethod
    def get_context() -> str:
        return """Chiquito de la Calzada es un famoso humorista español conocido 
        por su estilo único y su característico uso del lenguaje. Su humor se basa en juegos de palabras,
        chistes absurdos y una forma peculiar de contar historias.
        A menudo utiliza frases icónicas y expresiones cómicas que se han vuelto populares en la cultura española."""