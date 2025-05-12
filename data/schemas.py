from pydantic import BaseModel
from data.models import MarcaVehiculo

class VehiculoBase(BaseModel):
    marca: MarcaVehiculo
    modelo: str
    año: int

class VehiculoCreate(VehiculoBase):
    pass

class VehiculoRead(VehiculoBase):
    id: int
    class Config:
        orm_mode = True
