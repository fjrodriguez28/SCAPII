from enum import Enum

# Enum para campos de ordenamiento válidos
class GUsuariosOrderBy(str, Enum):
    USUARIO = "USUARIO"
    NOMBRE = "NOMBRE"
    NIVELSEG = "NIVELSEG"
    PUESTO = "PUESTO"
    LOGIN = "LOGIN"
