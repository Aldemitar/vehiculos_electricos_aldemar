from fastapi import HTTPException, status

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from data.enums import MarcaVehiculo
from data.models import Vehiculo, Bateria
from data.schemas import VehiculoUpdateForm, BateriaCreateForm

async def crear_vehiculo_db(vehiculo_create, session: AsyncSession):
    vehiculo = Vehiculo(**vehiculo_create.dict())
    session.add(vehiculo)
    await session.commit()
    await session.refresh(vehiculo) 
    return vehiculo

async def obtener_vehiculos_db(session: AsyncSession):
    result = await session.execute(select(Vehiculo))
    vehiculos = result.scalars().all()
    return vehiculos

async def eliminar_vehiculo_db(vehiculo_id: int, session: AsyncSession):
    result = await session.execute(select(Vehiculo).where(Vehiculo.id == vehiculo_id))
    vehiculo = result.scalar_one_or_none()

    if vehiculo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado.")

    await session.delete(vehiculo)
    await session.commit()
    return {"mensaje": f"Vehículo con ID {vehiculo_id} eliminado correctamente."}

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