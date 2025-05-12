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

class BateriaRead(BaseModel):
    id: int
    capacidad_kWh: float
    estado_salud: float
    ciclos_carga: int
    temperatura_operacion: Optional[float]
    vehiculo_id: Optional[int]

    class Config:
        orm_mode = True

class BateriaCreateForm:
    def __init__(
        self,
        capacidad_kWh: float = Form(...),
        estado_salud: float = Form(...),
        ciclos_carga: int = Form(...),
        temperatura_operacion: Optional[float] = Form(None),
    ):
        self.capacidad_kWh = capacidad_kWh
        self.estado_salud = estado_salud
        self.ciclos_carga = ciclos_carga
        self.temperatura_operacion = temperatura_operacion


class BateriaUpdateForm:
    def __init__(
        self,
        capacidad_kWh: Optional[float] = Form(None),
        estado_salud: Optional[float] = Form(None),
        ciclos_carga: Optional[int] = Form(None),
        temperatura_operacion: Optional[float] = Form(None),
        vehiculo_id: Optional[int] = Form(None),
    ):
        self.capacidad_kWh = capacidad_kWh
        self.estado_salud = estado_salud
        self.ciclos_carga = ciclos_carga
        self.temperatura_operacion = temperatura_operacion
        self.vehiculo_id = vehiculo_id

    def dict(self):
        return {
            k: v for k, v in self.__dict__.items() if v is not None
        }