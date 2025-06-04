from fastapi import HTTPException, status

from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from data.enums import MarcaVehiculo
from data.models import Vehiculo, Bateria
from data.schemas import VehiculoUpdateForm, BateriaCreateForm

from utils.supabase_db import save_file, supabase, SUPABASE_BUCKET, get_supabase_path_from_url

from typing import List, Optional

async def crear_vehiculo_db(vehiculo_create, session: AsyncSession):
    vehiculo = Vehiculo(**vehiculo_create.dict())
    session.add(vehiculo)
    await session.commit()
    await session.refresh(vehiculo) 
    return vehiculo

async def obtener_vehiculos_db(session: AsyncSession) -> List[Vehiculo]:
    result = await session.execute(select(Vehiculo).where(Vehiculo.eliminado == False))
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
    result = await session.execute(select(Vehiculo).where(Vehiculo.marca == marca))
    vehiculos = result.scalars().all()
    return vehiculos

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
    result = await session.execute(select(Bateria).where(Bateria.eliminado == False))
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