from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from data.enums import MarcaVehiculo, RolUsuario
from pydantic import validator, EmailStr
from datetime import date
from sqlalchemy import Column, Boolean, Enum

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

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, min_length=2, max_length=50)
    email: EmailStr = Field(unique=True, index=True)
    contraseña: str = Field(min_length=6)
    rol: RolUsuario = Field(sa_column=Column(Enum(RolUsuario), nullable=False))
    fecha_registro: date = Field(default_factory=date.today)
    activo: bool = Field(default=True, sa_column=Column(Boolean, default=True))
    eliminado: bool = Field(default=False, sa_column=Column(Boolean, default=False))
    @validator("contraseña")
    def validar_contraseña(cls, v):
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        return v

    @validator("nombre")
    def validar_nombre(cls, v):
        if not v.isalpha() and " " not in v:
            raise ValueError("El nombre solo puede contener letras y espacios.")
        return v