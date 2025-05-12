from sqlalchemy.future import select
from data.models import Vehiculo
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