from enum import Enum

class MarcaVehiculo(str, Enum):
    TESLA = "Tesla"
    NISSAN = "Nissan"
    BMW = "BMW"
    RENAULT = "Renault"
    CHEVROLET = "Chevrolet"

class EstadoSaludBateria(str, Enum):
    EXCELENTE = "Excelente"
    BUENO = "Bueno"
    REGULAR = "Regular"
    MALO = "Malo"

class RolUsuario(str, Enum):
    ADMIN = "admin"
    TECNICO = "tecnico"
    OPERADOR = "operador"
    VISOR = "visor" 