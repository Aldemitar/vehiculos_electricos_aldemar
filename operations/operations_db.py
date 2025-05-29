from fastapi import HTTPException, status

from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from data.enums import MarcaVehiculo
from data.models import Vehiculo, Bateria
from data.schemas import VehiculoUpdateForm, BateriaCreateForm

from typing import List

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado.")
    update_data = {
        "marca": vehiculo_update.marca,
        "modelo": vehiculo_update.modelo,
        "año": vehiculo_update.año
    }
    for key, value in update_data.items():
        if value is not None:
            setattr(vehiculo, key, value)

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

async def obtener_baterias_db(session: AsyncSession):
    result = await session.execute(select(Bateria))
    baterias = result.scalars().all()
    return baterias

async def eliminar_bateria_db(bateria_id: int, session: AsyncSession):
    result = await session.execute(select(Bateria).where(Bateria.id == bateria_id))
    bateria = result.scalar_one_or_none()

    if bateria is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batería no encontrada.")

    await session.delete(bateria)
    await session.commit()
    return {"mensaje": f"Batería con ID {bateria_id} eliminada correctamente."}

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
    query = select(Vehiculo).where(Vehiculo.bateria == None)
    result = await session.execute(query)
    return result.scalars().all()