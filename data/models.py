from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from data.enums import MarcaVehiculo
from pydantic import validator
from datetime import date
from sqlalchemy import Column, Boolean

class Vehiculo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    marca: MarcaVehiculo
    modelo: str
    año: int
    eliminado: bool = Field(default=False, sa_column=Column(Boolean, default=False))  # <-- nuevo campo
    bateria: Optional["Bateria"] = Relationship(back_populates="vehiculo")

class Bateria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    capacidad_kWh: float
    estado_salud: float = Field(gt=0, le=100, description="Porcentaje entre 0 y 100")
    ciclos_carga: Optional[int] = Field(default=0, ge=0)
    temperatura_operacion: Optional[float] = Field(default=None, description="Temperatura en grados Celsius")

    vehiculo_id: Optional[int] = Field(default=None, foreign_key="vehiculo.id")
    vehiculo: Optional[Vehiculo] = Relationship(back_populates="bateria")

    @validator("estado_salud")
    def validar_estado_salud(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("El estado de salud debe estar entre 0 y 100.")
        return v