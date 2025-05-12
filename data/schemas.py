from pydantic import BaseModel
from fastapi import Form
from data.models import MarcaVehiculo

class VehiculoBase(BaseModel):
    marca: MarcaVehiculo
    modelo: str
    año: int

class VehiculoCreateForm:
    def __init__(
        self,
        marca: MarcaVehiculo = Form(...),
        modelo: str = Form(...),
        año: int = Form(...),
    ):
        self.marca = marca
        self.modelo = modelo
        self.año = año

class VehiculoRead(VehiculoBase):
    id: int
    class Config:
        orm_mode = True
