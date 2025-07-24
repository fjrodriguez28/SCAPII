from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict
from decimal import Decimal
import datetime

class SPartesBase(BaseModel):    
    NUMPARTE: Optional[str] = Field(None, max_length=70,description="Número de parte único (máximo 70 chars, se convierte a mayúsculas)",examples=["PARTEA"])
    TIPOPARTE: Optional[str] = Field(None,max_length=10,description="Tipo de parte (máximo 10 chars)",examples=["MATERIALES"])
    NUMPARTECOM: Optional[str] = Field(None, max_length=70,description="Número de parte comercial (máximo 70 chars)")
    NUMPARTEREF: Optional[str] = Field(None, max_length=70,description="Número de parte de referencia (máximo 70 chars)")
    DESCRIPCIONE: Optional[str] = Field(None, max_length=500,description="Descripción en español (máximo 500 chars)")
    DESCRIPCIONI: Optional[str] = Field(None, max_length=500,description="Descripción en inglés (máximo 500 chars)")
    CLASE: Optional[str] = Field(None, max_length=8,description="Clase de la parte (máximo 8 chars, se convierte a mayúsculas)")
    UNIMED: Optional[str] = Field(None,max_length=5,description="Unidad de medida (máximo 5 chars, se convierte a mayúsculas)")
    UNIMEDEQUIV: Optional[str] = Field(None,max_length=5,description="Unidad de medida equivalente (máximo 5 chars)")
    FACTORCONV: Optional[Decimal] = Field(None, gt=0,description="Factor de conversión (debe ser positivo)")
    COSTOUNITARIO: Optional[Decimal] = Field(None, ge=0,description="Costo unitario (mayor o igual a 0)")
    TIPOMONEDA: Optional[str] = Field(None, max_length=2,description="Tipo de moneda (máximo 2 chars, se convierte a mayúsculas)")
    CLAVEMONEDA: Optional[str] = Field(None,max_length=3,description="Clave de moneda (máximo 3 chars, se convierte a mayúsculas)")
    PESOUNITARIO: Optional[Decimal] = Field(None, ge=0,description="Peso unitario (mayor o igual a 0)")
    TIPOMAT: Optional[str] = Field(None, max_length=10,description="Tipo de material (máximo 10 chars)")
    FRACCION: Optional[str] = Field(None, max_length=10,description="Fracción arancelaria (máximo 10 chars)")
    FRACCIONAME: Optional[str] = Field(None, max_length=16,description="Fracción americana (máximo 16 chars)")
    ADVALOREMAME: Optional[Decimal] = Field(None, ge=0,description="Ad valorem americano")
    FRACCAMEEXPONDUTY: Optional[str] = Field(None, max_length=16,description="Fracción americana exportación duty (máximo 16 chars)")
    FRACEUA: Optional[str] = Field(None, max_length=13,description="Fracción EUA (máximo 13 chars)")
    FRACCANADA: Optional[str] = Field(None, max_length=13,description="Fracción Canadá (máximo 13 chars)")
    SUBEMPRESA: Optional[str] = Field(None, max_length=5,description="Sub empresa (máximo 5 chars)")
    UMEXISTENCIA: Optional[str] = Field(None,max_length=5,description="UM existencia (máximo 5 chars)")    
    VALORAGREGADO: Optional[Decimal] = Field(None, ge=0, description="Valor agregado")
    TIPOVA: Optional[Literal["PO", "MN", "ME"]] = Field(None,description="Tipo VA: ME=Dólares, MN=Pesos, PO=Porcentaje (default: PO)")
    FECHAMODIFICA: Optional[int] = None
    UNIMEDALTERNA: Optional[str] = Field(None, max_length=5, description="UM alterna (máximo 5 chars)")
    CLAVEFDA: Optional[str] = Field(None, max_length=20, description="Clave FDA (máximo 20 chars)")
    LEYENDASEG: Optional[str] = Field(None, max_length=1500, description="Leyenda seguridad (máximo 1500 chars)")
    VALORNOORIG: Optional[Decimal] = None
    IMPPAGAR: Optional[Decimal] = None
    DESCESPSCRAP: Optional[str] = Field(None, max_length=499, description="Descripción ESP scrap (máximo 499 chars)")
    DESCINGSCRAP: Optional[str] = Field(None, max_length=499, description="Descripción ING scrap (máximo 499 chars)")
    FRACEXPOSCRAP: Optional[str] = Field(None, max_length=10, description="Fracción expo scrap (máximo 10 chars)")
    FRACAMESCRAP: Optional[str] = Field(None, max_length=16, description="Fracción AME scrap (máximo 16 chars)")
    FECHACOSTO: Optional[int] = None
    FOTOPARTE: Optional[str] = Field(None, max_length=255, description="Foto parte (máximo 255 chars)")
    CAPXUMAUXILIAR: Optional[str] = Field(None, max_length=1, description="Cap UM auxiliar (1 char)")
    FACTORAUXILIAR: Optional[Decimal] = None
    UMAUXILIAR: Optional[str] = Field(None, max_length=5, description="UM auxiliar (máximo 5 chars)")
    COSTOUAUXILIAR: Optional[Decimal] = None
    CAPTXKILO: Optional[str] = Field(None, max_length=1, description="Cap por kilo (1 char)")
    CANTKILO: Optional[Decimal] = None
    COSTOVENTA: Optional[Decimal] = None
    CANTPZXCJ: Optional[Decimal] = None
    VERSIONBILL: Optional[int] = None
    NUMPARTESUS: Optional[str] = Field(None, max_length=70, description="Número parte SUS (máximo 70 chars)")
    ESREPARACION: Optional[Literal["SI", "NO"]] = Field(None,description="Es reparación: SI/NO (default: NO)")
    COSTOUNITARIOREP: Optional[Decimal] = None
    USACANTALTERNA: Optional[int] = None
    FECHAMODBOM: Optional[int] = None
    FECHAMODFRACAME: Optional[int] = None
    VALORAGREGADOREP: Optional[Decimal] = None
    ESMATPELIGROSO: Optional[str] = Field(None, max_length=1, description="Es material peligroso (1 char)")
    NUMEMERGENCIA: Optional[str] = Field(None, max_length=30, description="Número emergencia (máximo 30 chars)")
    CLASEDEPELIGRO: Optional[str] = Field(None, max_length=4, description="Clase peligro (máximo 4 chars)")
    NUMIDENTIFICACIONUN: Optional[str] = Field(None, max_length=6, description="Número ID UN (máximo 6 chars)")
    GRUPOEMBALAJE: Optional[str] = Field(None, max_length=3, description="Grupo embalaje (máximo 3 chars)")
    NOMAPROPIADOEMB: Optional[str] = Field(None, max_length=500, description="Nomenclatura embalaje (máximo 500 chars)")
    NOTASMATPELIGROSO: Optional[str] = Field(None, max_length=499, description="Notas material peligroso (máximo 499 chars)")
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
    ESTEXTIL: Optional[str] = Field(None, max_length=2, description="Es textil (máximo 2 chars)")
    PROVEEDOR: Optional[str] = Field(None, max_length=8, description="Proveedor (máximo 8 chars)")
    ECCN: Optional[str] = Field(None, max_length=20, description="ECCN (máximo 20 chars)")
    SIMBOLOEXCLIC: Optional[str] = Field(None, max_length=19, description="Símbolo exc lic (máximo 19 chars)")
    CAMPOOPCIONAL: Optional[str] = Field(None, max_length=800, description="Campo opcional (máximo 800 chars)")
    UNIMEDEQUIV2: Optional[str] = Field(None, max_length=5, description="UM equiv 2 (máximo 5 chars)")
    FACTORCONV2: Optional[Decimal] = Field(None, gt=0,description="Factor conversión 2 (debe ser positivo)")
    LABORCOST: Optional[Decimal] = None
    EXPORTCODE: Optional[str] = Field(None, max_length=2, description="Código exportación (máximo 2 chars)")
    LICENSECODE: Optional[str] = Field(None, max_length=3, description="Código licencia (máximo 3 chars)")
    CAMPOOPCIONALBOM: Optional[str] = Field(None, max_length=200, description="Campo opcional BOM (máximo 200 chars)")
    TIPOPESO: Optional[Literal["KILOS", "LBS"]] = Field(None,description="Tipo peso: KILOS/LBS (default: KILOS)")
    TIPOIMMEX: Optional[str] = Field(None, max_length=20, description="Tipo IMMEX (máximo 20 chars)")
    CLAVEFCC: Optional[str] = Field(None, max_length=30, description="Clave FCC (máximo 30 chars)")
    NUMPARTESCRAP: Optional[str] = Field(None, max_length=70, description="Número parte scrap (máximo 70 chars)")
    NUMPARTEMERMA: Optional[str] = Field(None, max_length=70, description="Número parte merma (máximo 70 chars)")
    FACTORDESP: Optional[Decimal] = None
    HABILITADADESHABILITADA: Optional[int] = None
    FECHAMODIFICA_ISO: Optional[datetime.datetime] = Field(None, description="Fecha en formato ISO 8601",examples=["2024-07-18T15:09:02.199Z"])
    VERSIONBOM: Optional[int] = None
    ORDENVENTA: Optional[str] = Field(None, max_length=50, description="Orden venta (máximo 50 chars)")
    CLIENTEASIGNADO: Optional[str] = Field(None, max_length=50, description="Cliente asignado (máximo 50 chars)")
    ANCHURA: Optional[str] = Field(None, max_length=50, description="Anchura (máximo 50 chars)")
    ESPESOR: Optional[str] = Field(None, max_length=50, description="Espesor (máximo 50 chars)")
    SPEC: Optional[str] = Field(None, max_length=50, description="Especificación (máximo 50 chars)")
    FACTORCONVERSION: Optional[Decimal] = None
    UMCONVERSION: Optional[str] = Field(None, max_length=9, description="UM conversión (máximo 9 chars)")
    NOTIFICARSIPARTEUSAREGLA8VA: Optional[int] = None
    FECHACREACIONPARTE: Optional[int] = None
    LLENARINFOSUGERIDAR8: Optional[int] = None
    RESULTADOCALCULONAFTA: Optional[str] = Field(None, max_length=19, description="Resultado cálculo NAFTA (máximo 19 chars)")
    PORCENTAJECALCULONAFTA: Optional[Decimal] = None
    MDI: Optional[str] = Field(None, max_length=25, description="MDI (máximo 25 chars)")
    CONSECUTIVOATF: Optional[int] = None
    FRACCIONAMERICANASIFRA: Optional[str] = Field(None, max_length=19, description="Fracción americana SIFRA (máximo 19 chars)")
    NUMPARTEREFFLEX: Optional[str] = Field(None, max_length=120, description="Número parte ref flex (máximo 120 chars)")
    DTA: Optional[str] = Field(None, max_length=19, description="DTA (máximo 19 chars)")
    DTB: Optional[str] = Field(None, max_length=19, description="DTB (máximo 19 chars)")
    DTG: Optional[str] = Field(None, max_length=19, description="DTG (máximo 19 chars)")
    IDENTIFICADOR: Optional[str] = Field(None, max_length=1000, description="Identificador (máximo 1000 chars)")
    CONSECUTIVOAPHIS: Optional[int] = None        

    # Validadores personalizados adaptados de Zod    
    @field_validator('NUMPARTE','NUMPARTEREF', 'DESCRIPCIONE', 'DESCRIPCIONI', 'FRACCIONAME', 'CLASE', 'UNIMED',  mode='before')
    def validate_trim_fields(cls, v):
        """Trim espacios como en Zod"""
        if v is not None:
            return str(v).strip()
        return v
    
    @field_validator('NUMPARTE', 'CLASE', 'UNIMED', 'TIPOMONEDA', 'CLAVEMONEDA', mode='before')
    def validate_uppercase_fields(cls, v):
        """Trim y uppercase como en Zod"""
        if v is not None:
            return str(v).upper()
        return v
    
    @field_validator('COSTOUNITARIO', 'PESOUNITARIO', 'VALORAGREGADO', 'VALEMPAQUENAC', mode='before')
    def validate_parse_float(cls, v):
        """Convierte a float como parseFloat() en Zod"""
        if v is not None:
            try:
                return float(v)
            except (ValueError, TypeError):
                raise ValueError('Debe ser un número válido')
        return v
    
    @field_validator('TIPOVA', mode='before')
    def validate_tipova(cls, v):
        """Validación específica de TIPOVA como en Zod"""
        if v is None or (isinstance(v, str) and v.strip() == ''):
            return None
        v = str(v).upper()
        if v not in ['PO', 'MN', 'ME']:
            raise ValueError('Capturar una opción valida: ME para Dolares, MN para Pesos, PO para Porcentaje o dejar el campo vacio y automaticamente se asigna Porcentaje.')
        return v
    
    @field_validator('ESREPARACION', mode='before')
    def validate_esreparacion(cls, v):
        """Validación específica de ESREPARACION como en Zod"""
        if v is None or (isinstance(v, str) and v.strip() == ''):
            return None
        v = str(v).upper()
        if v not in ['SI', 'NO']:
            raise ValueError('El campo ESREPARACION debe ser "Si" o "No" o dejarlo vacío para que se asigne "No" por defecto.')
        return v
    
    @field_validator('TIPOPESO', mode='before')
    def validate_tipopeso(cls, v):
        """Validación específica de TIPOPESO como en Zod"""
        if v is None or (isinstance(v, str) and v.strip() == ''):
            return None
        v = str(v).upper()
        if v not in ['KILOS', 'LBS']:
            raise ValueError('Capturar una opción valida: KILOS, LIBRAS o dejar el campo vacio y automaticamente se asigna KILOS.')
        return v
    
    @field_validator('FACTORCONV', 'FACTORCONV2', mode='before')
    def validate_positive_factors(cls, v):
        """Validación de números positivos como en Zod"""
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

# Schema para crear usuario
class SPartesCreate(SPartesBase):
    NUMPARTE: str

# Schema para actualizar usuario
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

    