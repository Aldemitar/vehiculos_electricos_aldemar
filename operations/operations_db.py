from sqlalchemy.future import select
from data.models import Vehiculo
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

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