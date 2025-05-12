from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from data.enums import MarcaVehiculo
from pydantic import validator

class Vehiculo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    marca: MarcaVehiculo
    modelo: str
    año: int
    bateria: Optional["Bateria"] = Relationship(back_populates="vehiculo")

class Bateria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    capacidad_kWh: float
    estado_salud: float = Field(gt=0, le=100, description="Porcentaje entre 0 y 100")
    vehiculo_id: Optional[int] = Field(default=None, foreign_key="vehiculo.id")

    vehiculo: Optional[Vehiculo] = Relationship(back_populates="bateria")

    @validator("estado_salud")
    def validar_estado_salud(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("El estado de salud debe estar entre 0 y 100.")
        return v