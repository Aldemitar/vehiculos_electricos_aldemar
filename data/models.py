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
    imagen_url: Optional[str] = Field(default=None, description="URL de la imagen del vehículo") 
    eliminado: bool = Field(default=False, sa_column=Column(Boolean, default=False))
    bateria: Optional["Bateria"] = Relationship(back_populates="vehiculo", sa_relationship_kwargs={"uselist": False})

class Bateria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    capacidad_kWh: float
    estado_salud: float = Field(gt=0, le=100)
    ciclos_carga: Optional[int] = Field(default=0, ge=0)
    temperatura_operacion: Optional[float] = Field(default=None)
    vehiculo_id: Optional[int] = Field(default=None, foreign_key="vehiculo.id")
    vehiculo: Optional[Vehiculo] = Relationship(back_populates="bateria")
    
    eliminado: bool = Field(default=False)

    @validator("estado_salud")
    def validar_estado_salud(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("El estado de salud debe estar entre 0 y 100.")
        return v