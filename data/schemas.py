from pydantic import BaseModel, EmailStr
from fastapi import Form, UploadFile, File
from data.models import MarcaVehiculo, RolUsuario
from typing import Optional
from datetime import date

class VehiculoBase(BaseModel):
    marca: MarcaVehiculo
    modelo: str
    año: int
    imagen_url: Optional[str] = None 

class VehiculoCreate(VehiculoBase):
    pass

class VehiculoCreateForm:
    def __init__(
        self,
        marca: MarcaVehiculo = Form(...),
        modelo: str = Form(...),
        año: int = Form(...),
        imagen: Optional[UploadFile] = File(None),
    ):
        self.marca = marca
        self.modelo = modelo
        self.año = año
        self.imagen = imagen

class VehiculoRead(VehiculoBase):
    id: int
    class Config:
        from_attributes = True

class VehiculoUpdateForm:
    def __init__(
        self,
        marca: Optional[MarcaVehiculo] = Form(None),
        modelo: Optional[str] = Form(None),
        año: Optional[int] = Form(None),
        imagen: Optional[UploadFile] = File(None)
    ):
        self.marca = marca
        self.modelo = modelo
        self.año = año
        self.imagen = imagen

class BateriaRead(BaseModel):
    id: int
    capacidad_kWh: float
    estado_salud: float
    ciclos_carga: int
    temperatura_operacion: Optional[float]
    vehiculo_id: Optional[int]

    class Config:
        from_attributes = True

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

class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    rol: RolUsuario

class UsuarioCreate(UsuarioBase):
    contraseña: str
    activo: bool = True

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    contraseña: Optional[str] = None
    rol: Optional[RolUsuario] = None
    activo: Optional[bool] = None

class UsuarioResponse(UsuarioBase):
    id: int
    activo: bool
    eliminado: bool
    fecha_registro: date

    class Config:
        from_attributes = True

class UsuarioCreateForm:
    def __init__(
        self,
        nombre: str = Form(..., min_length=2, max_length=50),
        email: EmailStr = Form(...),
        contraseña: str = Form(..., min_length=6),
        rol: RolUsuario = Form(...),
        activo: bool = Form(True)
    ):
        self.nombre = nombre
        self.email = email
        self.contraseña = contraseña
        self.rol = rol
        self.activo = activo

class UsuarioUpdateForm:
    def __init__(
        self,
        nombre: str = Form(..., min_length=2, max_length=50),
        email: EmailStr = Form(...),
        contraseña: Optional[str] = Form(None),
        rol: RolUsuario = Form(...),
        activo: bool = Form(False)
    ):
        self.nombre = nombre
        self.email = email
        self.contraseña = contraseña if contraseña and len(contraseña) > 0 else None
        self.rol = rol
        self.activo = activo
    
    def dict(self, exclude_unset=False):
        data = {
            "nombre": self.nombre,
            "email": self.email,
            "rol": self.rol,
            "activo": self.activo
        }
        if self.contraseña:
            data["contraseña"] = self.contraseña
        return data