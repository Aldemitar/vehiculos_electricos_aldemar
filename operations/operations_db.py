from fastapi import HTTPException, status

from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from data.enums import MarcaVehiculo, RolUsuario
from data.models import Vehiculo, Bateria, Usuario
from data.schemas import VehiculoUpdateForm, BateriaCreateForm, UsuarioCreateForm, UsuarioUpdateForm, UsuarioCreate

from utils.supabase_db import save_file, supabase, SUPABASE_BUCKET, get_supabase_path_from_url

from typing import List, Optional

from passlib.context import CryptContext

async def crear_vehiculo_db(vehiculo_create, session: AsyncSession):
    vehiculo = Vehiculo(**vehiculo_create.dict())
    session.add(vehiculo)
    await session.commit()
    await session.refresh(vehiculo) 
    return vehiculo

async def obtener_vehiculos_db(session: AsyncSession) -> List[Vehiculo]:
    result = await session.execute(select(Vehiculo).where(Vehiculo.eliminado == False).order_by(Vehiculo.id))
    return result.scalars().all()

async def eliminar_vehiculo_db(vehiculo_id: int, session: AsyncSession):
    result = await session.execute(select(Vehiculo).where(Vehiculo.id == vehiculo_id))
    vehiculo = result.scalar_one_or_none()

    if vehiculo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado.")

    vehiculo.eliminado = True
    await session.commit()
    return {"mensaje": f"Vehículo con ID {vehiculo_id} marcado como eliminado."}

async def filtrar_vehiculos_por_marca_db(marca: MarcaVehiculo, session: AsyncSession):
    query = select(Vehiculo).where(Vehiculo.marca == marca,Vehiculo.eliminado == False).order_by(Vehiculo.id)
    result = await session.execute(query)
    return result.scalars().all()

async def actualizar_vehiculo_db_form(vehiculo_id: int, vehiculo_update: VehiculoUpdateForm, session: AsyncSession):
    result = await session.execute(select(Vehiculo).where(Vehiculo.id == vehiculo_id))
    vehiculo = result.scalar_one_or_none()
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    imagen_actual = vehiculo.imagen_url
    nueva_imagen_url: Optional[str] = None
    if vehiculo_update.imagen:
        resultado = await save_file(vehiculo_update.imagen, to_supabase=True)

        if "url" in resultado:
            nueva_imagen_url = resultado["url"]
            if imagen_actual:
                path_antiguo = get_supabase_path_from_url(imagen_actual, SUPABASE_BUCKET)
                supabase.storage.from_(SUPABASE_BUCKET).remove([path_antiguo])
        else:
            print("Error al subir nueva imagen:", resultado.get("error"))
    for campo in ["marca", "modelo", "año"]:
        valor = getattr(vehiculo_update, campo)
        if valor is not None:
            setattr(vehiculo, campo, valor)
    if nueva_imagen_url:
        vehiculo.imagen_url = nueva_imagen_url

    session.add(vehiculo)
    await session.commit()
    await session.refresh(vehiculo)
    return vehiculo

async def crear_bateria_db(bateria_create: BateriaCreateForm, session: AsyncSession):
    bateria = Bateria(**bateria_create.__dict__)
    session.add(bateria)
    await session.commit()
    await session.refresh(bateria)
    return bateria

async def obtener_baterias_db(session: AsyncSession) -> List[Bateria]:
    result = await session.execute(select(Bateria).where(Bateria.eliminado == False).order_by(Bateria.id))
    return result.scalars().all()

async def eliminar_bateria_db(bateria_id: int, session: AsyncSession):
    result = await session.execute(select(Bateria).where(Bateria.id == bateria_id))
    bateria = result.scalar_one_or_none()

    if not bateria:
        raise HTTPException(status_code=404, detail="Batería no encontrada")

    bateria.eliminado = True
    await session.commit()

async def obtener_baterias_eliminadas_db(session: AsyncSession) -> List[Bateria]:
    result = await session.execute(select(Bateria).where(Bateria.eliminado == True))
    return result.scalars().all()

async def actualizar_bateria_db(bateria_id: int, bateria_data, session: AsyncSession):
    result = await session.execute(select(Bateria).where(Bateria.id == bateria_id))
    bateria = result.scalar_one_or_none()
    if not bateria:
        raise HTTPException(status_code=404, detail="Batería no encontrada")

    for field, value in bateria_data.dict().items():
        setattr(bateria, field, value)

    await session.commit()
    await session.refresh(bateria)
    return bateria

async def asociar_bateria_a_vehiculo_db(bateria_id: int, vehiculo_id: int, session: AsyncSession):
    result_bateria = await session.execute(select(Bateria).where(Bateria.id == bateria_id))
    bateria = result_bateria.scalar_one_or_none()
    if not bateria:
        raise HTTPException(status_code=404, detail="Batería no encontrada")

    result_vehiculo = await session.execute(select(Vehiculo).where(Vehiculo.id == vehiculo_id))
    vehiculo = result_vehiculo.scalar_one_or_none()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    bateria.vehiculo_id = vehiculo_id
    await session.commit()
    await session.refresh(bateria)
    return bateria

async def obtener_dashboard_metricas(session: AsyncSession):
    total_vehiculos = await session.scalar(select(func.count(Vehiculo.id)))
    total_baterias = await session.scalar(select(func.count(Bateria.id)))
    baterias_mal_estado = await session.scalar(
        select(func.count(Bateria.id)).where(Bateria.estado_salud < 30)
    )

    porcentaje_mal_estado = (
        (baterias_mal_estado / total_baterias * 100) if total_baterias else 0
    )

    return {
        "total_vehiculos": total_vehiculos,
        "total_baterias": total_baterias,
        "baterias_en_mal_estado": baterias_mal_estado,
        "porcentaje_mal_estado": round(porcentaje_mal_estado, 2)
    }

async def obtener_vehiculos_con_bateria(session: AsyncSession):
    query = select(Vehiculo).where(Vehiculo.bateria != None)
    result = await session.execute(query)
    return result.scalars().all()

async def obtener_vehiculos_sin_bateria(session: AsyncSession):
    stmt = (
        select(Vehiculo)
        .outerjoin(Bateria, Vehiculo.id == Bateria.vehiculo_id)
        .where(Bateria.id == None, Vehiculo.eliminado == False)
    )
    result = await session.execute(stmt)
    return result.scalars().all()

async def buscar_bateria_por_id_db(bateria_id: int, session: AsyncSession) -> Optional[Bateria]:
    result = await session.execute(select(Bateria).where(Bateria.id == bateria_id, Bateria.eliminado == False))
    return result.scalar_one_or_none()

async def obtener_vehiculo_por_id(session: AsyncSession, vehiculo_id: int):
    result = await session.execute(
        select(Vehiculo).where(Vehiculo.id == vehiculo_id, Vehiculo.eliminado == False)
    )
    return result.scalar_one_or_none()

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from typing import List, Optional
import bcrypt

# Función auxiliar para hashear contraseñas
def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña coincide con el hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Operaciones CRUD para Usuarios

async def crear_usuario_db(usuario_create: UsuarioCreate, session: AsyncSession):
    usuario = Usuario(**usuario_create.dict())
    session.add(usuario)
    await session.commit()
    await session.refresh(usuario)
    return usuario

async def obtener_usuarios_db(session: AsyncSession) -> List[Usuario]:
    result = await session.execute(
        select(Usuario).where(Usuario.eliminado == False).order_by(Usuario.id)
    )
    return result.scalars().all()

async def obtener_usuario_por_id(session: AsyncSession, usuario_id: int) -> Optional[Usuario]:
    result = await session.execute(
        select(Usuario).where(Usuario.id == usuario_id, Usuario.eliminado == False)
    )
    return result.scalar_one_or_none()

async def obtener_usuario_por_email(session: AsyncSession, email: str) -> Optional[Usuario]:
    result = await session.execute(
        select(Usuario).where(Usuario.email == email, Usuario.eliminado == False)
    )
    return result.scalar_one_or_none()

async def filtrar_usuarios_por_rol_db(rol: str, session: AsyncSession) -> List[Usuario]:
    try:
        rol_enum = RolUsuario(rol)
        result = await session.execute(
            select(Usuario).where(
                Usuario.rol == rol_enum,
                Usuario.eliminado == False
            ).order_by(Usuario.id)
        )
        return result.scalars().all()
    except ValueError:
        return []

async def eliminar_usuario_db(usuario_id: int, session: AsyncSession):
    result = await session.execute(select(Usuario).where(Usuario.id == usuario_id))
    usuario = result.scalar_one_or_none()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.eliminado = True
    await session.commit()
    return {"message": "Usuario eliminado correctamente"}

async def obtener_usuarios_eliminados_db(session: AsyncSession) -> List[Usuario]:
    result = await session.execute(
        select(Usuario).where(Usuario.eliminado == True).order_by(Usuario.id)
    )
    return result.scalars().all()

async def restaurar_usuario_db(usuario_id: int, session: AsyncSession):
    result = await session.execute(select(Usuario).where(Usuario.id == usuario_id))
    usuario = result.scalar_one_or_none()
    if not usuario or not usuario.eliminado:
        raise HTTPException(
            status_code=404, 
            detail="Usuario no encontrado o ya está activo"
        )
    usuario.eliminado = False
    await session.commit()
    return {"message": "Usuario restaurado correctamente"}

async def actualizar_usuario_db(usuario_id: int, usuario_data, session: AsyncSession):
    result = await session.execute(select(Usuario).where(Usuario.id == usuario_id))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    for field, value in usuario_data.dict(exclude_unset=True).items():
        if value is not None:
            if field == "contraseña" and value:
                value = hash_password(value)
            setattr(usuario, field, value)

    await session.commit()
    await session.refresh(usuario)
    return usuario

async def actualizar_usuario_db_form(usuario_id: int, usuario_update: UsuarioUpdateForm, session: AsyncSession):
    result = await session.execute(select(Usuario).where(Usuario.id == usuario_id))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario_update.nombre:
        usuario.nombre = usuario_update.nombre
    if usuario_update.email:
        existing = await obtener_usuario_por_email(session, usuario_update.email)
        if existing and existing.id != usuario_id:
            raise HTTPException(status_code=400, detail="El email ya está en uso")
        usuario.email = usuario_update.email
    if usuario_update.rol:
        usuario.rol = usuario_update.rol
    if usuario_update.contraseña and len(usuario_update.contraseña) > 0:
        usuario.contraseña = hash_password(usuario_update.contraseña)
    usuario.activo = usuario_update.activo if hasattr(usuario_update, 'activo') else usuario.activo

    await session.commit()
    await session.refresh(usuario)
    return usuario

async def toggle_usuario_activo_db(usuario_id: int, session: AsyncSession):
    result = await session.execute(select(Usuario).where(Usuario.id == usuario_id))
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario.activo = not usuario.activo
    await session.commit()
    return {"message": f"Usuario {'activado' if usuario.activo else 'desactivado'} correctamente"}

async def contar_usuarios_por_rol(session: AsyncSession) -> dict:
    result = await session.execute(
        select(Usuario).where(Usuario.eliminado == False)
    )
    usuarios = result.scalars().all()
    
    conteo = {}
    for usuario in usuarios:
        rol_nombre = usuario.rol.value
        conteo[rol_nombre] = conteo.get(rol_nombre, 0) + 1
    
    return conteo

async def verificar_credenciales(email: str, password: str, session: AsyncSession) -> Optional[Usuario]:
    usuario = await obtener_usuario_por_email(session, email)
    
    if not usuario:
        return None
    
    if not usuario.activo:
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    
    if verify_password(password, usuario.contraseña):
        return usuario
    
    return None