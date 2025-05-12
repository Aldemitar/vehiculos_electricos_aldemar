from pydantic import BaseModel
from fastapi import Form
from data.models import MarcaVehiculo
from typing import Optional

class VehiculoBase(BaseModel):
    marca: MarcaVehiculo
    modelo: str
    año: int

class VehiculoCreate(VehiculoBase):
    pass

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

class VehiculoUpdateForm:
    def __init__(
        self,
        marca: Optional[MarcaVehiculo] = Form(None),
        modelo: Optional[str] = Form(None),
        año: Optional[int] = Form(None)
    ):
        self.marca = marca
        self.modelo = modelo
        self.año = año