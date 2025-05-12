from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class Bateria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    capacidad_kWh: float
    estado_salud: float  # porcentaje 0-100
    vehiculo_id: Optional[int] = Field(default=None, foreign_key="vehiculo.id")

class Vehiculo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    marca: str
    modelo: str
    año: int
    bateria: Optional[Bateria] = Relationship(back_populates="vehiculo")

Bateria.vehiculo = Relationship(back_populates="bateria")
