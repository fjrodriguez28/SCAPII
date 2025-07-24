from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict
from decimal import Decimal
import datetime

class SPartesBase(BaseModel):    
    NUMPARTE: Optional[str] = Field(None, max_length=70,description="Número de parte único",examples=["PARTEA"])
    TIPOPARTE: Optional[str] = Field(None,max_length=10,description="Tipo de parte",examples=["MATERIALES"])
    NUMPARTECOM: Optional[str] = Field(None, max_length=70,description="Número de parte comercial")
    NUMPARTEREF: Optional[str] = Field(None, max_length=70,description="Número de parte de referencia")
    DESCRIPCIONE: Optional[str] = Field(None, max_length=500,description="Descripción en español")
    DESCRIPCIONI: Optional[str] = Field(None, max_length=500,description="Descripción en inglés")
    CLASE: Optional[str] = Field(None, max_length=8,description="Clase de la parte")
    UNIMED: Optional[str] = Field(None,max_length=5,description="Unidad de medida")
    UNIMEDEQUIV: Optional[str] = Field(None,max_length=5,description="Unidad de medida equivalente")
    FACTORCONV: Optional[Decimal] = Field(None, gt=0,description="Factor de conversión")
    COSTOUNITARIO: Optional[Decimal] = Field(None, ge=0,description="Costo unitario")
    TIPOMONEDA: Optional[str] = Field(None, max_length=2,description="Tipo de moneda")
    CLAVEMONEDA: Optional[str] = Field(None,max_length=3,description="Clave de moneda")
    PESOUNITARIO: Optional[Decimal] = Field(None, ge=0,description="Peso unitario")
    TIPOMAT: Optional[str] = Field(None, max_length=10,description="Tipo de material")
    FRACCION: Optional[str] = Field(None, max_length=10,description="Fracción arancelaria")
    FRACCIONAME: Optional[str] = Field(None, max_length=16,description="Fracción americana")
    ADVALOREMAME: Optional[Decimal] = Field(None, ge=0,description="Ad valorem americano")
    FRACCAMEEXPONDUTY: Optional[str] = Field(None, max_length=16,description="Fracción americana exportación duty")
    FRACEUA: Optional[str] = Field(None, max_length=13,description="Fracción EUA")
    FRACCANADA: Optional[str] = Field(None, max_length=13,description="Fracción Canadá")
    SUBEMPRESA: Optional[str] = Field(None, max_length=5,description="Sub empresa")
    UMEXISTENCIA: Optional[str] = Field(None,max_length=5,description="UM existencia")    
    VALORAGREGADO: Optional[Decimal] = Field(None, ge=0, description="Valor agregado")
    TIPOVA: Optional[Literal["PO", "MN", "ME"]] = Field(None,description="Tipo VA: ME=Dólares, MN=Pesos, PO=Porcentaje (default: PO)")
    FECHAMODIFICA: Optional[int] = None
    UNIMEDALTERNA: Optional[str] = Field(None, max_length=5, description="UM alterna")
    CLAVEFDA: Optional[str] = Field(None, max_length=20, description="Clave FDA")
    LEYENDASEG: Optional[str] = Field(None, max_length=1500, description="Leyenda seguridad")
    VALORNOORIG: Optional[Decimal] = None
    IMPPAGAR: Optional[Decimal] = None
    DESCESPSCRAP: Optional[str] = Field(None, max_length=499, description="Descripción ESP scrap")
    DESCINGSCRAP: Optional[str] = Field(None, max_length=499, description="Descripción ING scrap")
    FRACEXPOSCRAP: Optional[str] = Field(None, max_length=10, description="Fracción expo scrap")
    FRACAMESCRAP: Optional[str] = Field(None, max_length=16, description="Fracción AME scrap")
    FECHACOSTO: Optional[int] = None
    FOTOPARTE: Optional[str] = Field(None, max_length=255, description="Foto parte")
    CAPXUMAUXILIAR: Optional[str] = Field(None, max_length=1, description="Cap UM auxiliar")
    FACTORAUXILIAR: Optional[Decimal] = None
    UMAUXILIAR: Optional[str] = Field(None, max_length=5, description="UM auxiliar")
    COSTOUAUXILIAR: Optional[Decimal] = None
    CAPTXKILO: Optional[str] = Field(None, max_length=1, description="Cap por kilo")
    CANTKILO: Optional[Decimal] = None
    COSTOVENTA: Optional[Decimal] = None
    CANTPZXCJ: Optional[Decimal] = None
    VERSIONBILL: Optional[int] = None
    NUMPARTESUS: Optional[str] = Field(None, max_length=70, description="Número parte SUS")
    ESREPARACION: Optional[Literal["SI", "NO"]] = Field(None,description="Es reparación: SI/NO (default: NO)")
    COSTOUNITARIOREP: Optional[Decimal] = None
    USACANTALTERNA: Optional[int] = None
    FECHAMODBOM: Optional[int] = None
    FECHAMODFRACAME: Optional[int] = None
    VALORAGREGADOREP: Optional[Decimal] = None
    ESMATPELIGROSO: Optional[str] = Field(None, max_length=1, description="Es material peligroso")
    NUMEMERGENCIA: Optional[str] = Field(None, max_length=30, description="Número emergencia")
    CLASEDEPELIGRO: Optional[str] = Field(None, max_length=4, description="Clase peligro")
    NUMIDENTIFICACIONUN: Optional[str] = Field(None, max_length=6, description="Número ID UN")
    GRUPOEMBALAJE: Optional[str] = Field(None, max_length=3, description="Grupo embalaje")
    NOMAPROPIADOEMB: Optional[str] = Field(None, max_length=500, description="Nomenclatura embalaje")
    NOTASMATPELIGROSO: Optional[str] = Field(None, max_length=499, description="Notas material peligroso")
    VALORDUTY: Optional[Decimal] = None
    FLETEDUTY: Optional[Decimal] = None
    VALORTOTALDUTY: Optional[Decimal] = None
    VALORNODUTY: Optional[Decimal] = None
    FLETENODUTY: Optional[Decimal] = None
    VALORTOTALNDUTY: Optional[Decimal] = None
    VALORTOTAL: Optional[Decimal] = None
    TRABAJODIREC: Optional[Decimal] = None
    GASTOGRALES: Optional[Decimal] = None
    OTROSGASTOS: Optional[Decimal] = None
    TOTALGASTOS: Optional[Decimal] = None
    DEPRECIACION: Optional[Decimal] = None
    TOOLING: Optional[Decimal] = None
    MATCONSUMED: Optional[Decimal] = None
    VALORSCRAP: Optional[Decimal] = None
    FORENGDESDEV: Optional[Decimal] = None
    VALTOTALASIST: Optional[Decimal] = None
    VALEMPAQUEFOR: Optional[Decimal] = None
    GANANCIA: Optional[Decimal] = None
    DUTIABLEVALUE7: Optional[Decimal] = None
    OTROSNDUTIABLE: Optional[Decimal] = None
    COSTOESTIMADO: Optional[Decimal] = None
    TOTALNDUTIABLE: Optional[Decimal] = None
    ACTUALDUTIABLE: Optional[Decimal] = None
    VALEMPAQUEUS: Optional[Decimal] = None
    VALEMPAQUENAC: Optional[Decimal] = None
    FECHACOSTOAME: Optional[int] = None
    ESTEXTIL: Optional[str] = Field(None, max_length=2, description="Es textil")
    PROVEEDOR: Optional[str] = Field(None, max_length=8, description="Proveedor")
    ECCN: Optional[str] = Field(None, max_length=20, description="ECCN")
    SIMBOLOEXCLIC: Optional[str] = Field(None, max_length=19, description="Símbolo exc lic")
    CAMPOOPCIONAL: Optional[str] = Field(None, max_length=800, description="Campo opcional")
    UNIMEDEQUIV2: Optional[str] = Field(None, max_length=5, description="UM equiv 2")
    FACTORCONV2: Optional[Decimal] = Field(None, gt=0,description="Factor conversión 2")
    LABORCOST: Optional[Decimal] = None
    EXPORTCODE: Optional[str] = Field(None, max_length=2, description="Código exportación")
    LICENSECODE: Optional[str] = Field(None, max_length=3, description="Código licencia")
    CAMPOOPCIONALBOM: Optional[str] = Field(None, max_length=200, description="Campo opcional BOM")
    TIPOPESO: Optional[Literal["KILOS", "LBS"]] = Field(None,description="Tipo peso: KILOS/LBS (default: KILOS)")
    TIPOIMMEX: Optional[str] = Field(None, max_length=20, description="Tipo IMMEX")
    CLAVEFCC: Optional[str] = Field(None, max_length=30, description="Clave FCC")
    NUMPARTESCRAP: Optional[str] = Field(None, max_length=70, description="Número parte scrap")
    NUMPARTEMERMA: Optional[str] = Field(None, max_length=70, description="Número parte merma")
    FACTORDESP: Optional[Decimal] = None
    HABILITADADESHABILITADA: Optional[int] = None
    FECHAMODIFICA_ISO: Optional[datetime.datetime] = Field(None, description="Fecha en formato ISO 8601",examples=["2024-07-18T15:09:02.199Z"])
    VERSIONBOM: Optional[int] = None
    ORDENVENTA: Optional[str] = Field(None, max_length=50, description="Orden venta")
    CLIENTEASIGNADO: Optional[str] = Field(None, max_length=50, description="Cliente asignado")
    ANCHURA: Optional[str] = Field(None, max_length=50, description="Anchura")
    ESPESOR: Optional[str] = Field(None, max_length=50, description="Espesor")
    SPEC: Optional[str] = Field(None, max_length=50, description="Especificación")
    FACTORCONVERSION: Optional[Decimal] = None
    UMCONVERSION: Optional[str] = Field(None, max_length=9, description="UM conversión")
    NOTIFICARSIPARTEUSAREGLA8VA: Optional[int] = None
    FECHACREACIONPARTE: Optional[int] = None
    LLENARINFOSUGERIDAR8: Optional[int] = None
    RESULTADOCALCULONAFTA: Optional[str] = Field(None, max_length=19, description="Resultado cálculo NAFTA")
    PORCENTAJECALCULONAFTA: Optional[Decimal] = None
    MDI: Optional[str] = Field(None, max_length=25, description="MDI")
    CONSECUTIVOATF: Optional[int] = None
    FRACCIONAMERICANASIFRA: Optional[str] = Field(None, max_length=19, description="Fracción americana SIFRA")
    NUMPARTEREFFLEX: Optional[str] = Field(None, max_length=120, description="Número parte ref flex")
    DTA: Optional[str] = Field(None, max_length=19, description="DTA")
    DTB: Optional[str] = Field(None, max_length=19, description="DTB")
    DTG: Optional[str] = Field(None, max_length=19, description="DTG")
    IDENTIFICADOR: Optional[str] = Field(None, max_length=1000, description="Identificador")
    CONSECUTIVOAPHIS: Optional[int] = None        

    # Validadores personalizados   
    @field_validator('NUMPARTE','NUMPARTEREF', 'DESCRIPCIONE', 'DESCRIPCIONI', 'FRACCIONAME', 'CLASE', 'UNIMED',  mode='before')
    def validate_trim_fields(cls, v):
        """Quitar espacios"""
        if v is not None:
            return str(v).strip()
        return v
    
    @field_validator('NUMPARTE', 'CLASE', 'UNIMED', 'TIPOMONEDA', 'CLAVEMONEDA', mode='before')
    def validate_uppercase_fields(cls, v):
        """Hacer mayúsculas"""
        if v is not None:
            return str(v).upper()
        return v
    
    @field_validator('COSTOUNITARIO', 'PESOUNITARIO', 'VALORAGREGADO', 'VALEMPAQUENAC', mode='before')
    def validate_parse_float(cls, v):
        """Convierte a float y valida"""
        if v is not None:
            try:
                return float(v)
            except (ValueError, TypeError):
                raise ValueError('Debe ser un número válido')
        return v
    
    @field_validator('TIPOVA', mode='before')
    def validate_tipova(cls, v):
        """ Valiación de valores de TIPOVA """
        if v is None or (isinstance(v, str) and v.strip() == ''):
            return None
        v = str(v).upper()
        if v not in ['PO', 'MN', 'ME']:
            raise ValueError('Capturar una opción valida: ME para Dolares, MN para Pesos, PO para Porcentaje o dejar el campo vacio y automaticamente se asigna Porcentaje.')
        return v
    
    @field_validator('ESREPARACION', mode='before')
    def validate_esreparacion(cls, v):
        """Validacion de valores de ESREPARACION"""
        if v is None or (isinstance(v, str) and v.strip() == ''):
            return None
        v = str(v).upper()
        if v not in ['SI', 'NO']:
            raise ValueError('El campo ESREPARACION debe ser "Si" o "No" o dejarlo vacío para que se asigne "No" por defecto.')
        return v
    
    @field_validator('TIPOPESO', mode='before')
    def validate_tipopeso(cls, v):
        """Validación de valores de TIPOPESO"""
        if v is None or (isinstance(v, str) and v.strip() == ''):
            return None
        v = str(v).upper()
        if v not in ['KILOS', 'LBS']:
            raise ValueError('Capturar una opción valida: KILOS, LIBRAS o dejar el campo vacio y automaticamente se asigna KILOS.')
        return v
    
    @field_validator('FACTORCONV', 'FACTORCONV2', mode='before')
    def validate_positive_factors(cls, v):
        """Validación de números positivos"""
        if v is not None:
            try:
                val = float(v)
                if val <= 0:
                    field_name = 'FACTORCONV' if 'FACTORCONV' in str(v) else 'FACTORCONV2'
                    raise ValueError(f'El campo {field_name} debe ser un número positivo.')
                return val
            except (ValueError, TypeError):
                raise ValueError('Debe ser un número válido')
        return v

# Schema para crear la parte
class SPartesCreate(SPartesBase):
    NUMPARTE: str

# Schema para actualizar la parte
class SPartesUpdate(SPartesBase):
    model_config = ConfigDict(
        exclude={'NUMPARTE'},        
    )

# Schema para respuesta (lo que devuelve la API)
class SPartes(SPartesBase):
    NUMPARTE: str
    
    model_config = ConfigDict(
        from_attributes=True
    )

    