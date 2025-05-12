from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status

from utils.connection_db import init_db, get_session

from data.models import Vehiculo, Bateria
from data.schemas import VehiculoCreateForm, VehiculoRead, VehiculoCreate, VehiculoUpdateForm, BateriaCreateForm, BateriaRead, BateriaUpdateForm
from data.enums import MarcaVehiculo

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from typing import List

from operations.operations_db import (
    crear_vehiculo_db,
    obtener_vehiculos_db,
    eliminar_vehiculo_db,
    filtrar_vehiculos_por_marca_db,
    actualizar_vehiculo_db_form,
    crear_bateria_db,
    obtener_baterias_db,
    eliminar_bateria_db,
    actualizar_bateria_db,
    asociar_bateria_a_vehiculo_db,
    obtener_dashboard_metricas,
    obtener_vehiculos_con_bateria,
    obtener_vehiculos_sin_bateria
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

from fastapi import Depends, status, Form
from data.schemas import VehiculoCreate, VehiculoRead, VehiculoCreateForm
from operations.operations_db import crear_vehiculo_db

@app.post("/vehiculos/form", response_model=VehiculoRead, status_code=status.HTTP_201_CREATED, tags=["Vehículos"])
async def crear_vehiculo_formulario(
    vehiculo_form: VehiculoCreateForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    vehiculo_create = VehiculoCreate(
        marca=vehiculo_form.marca,
        modelo=vehiculo_form.modelo,
        año=vehiculo_form.año
    )
    return await crear_vehiculo_db(vehiculo_create, session)

@app.get("/vehiculos", response_model=List[VehiculoRead], tags=["Vehículos"])
async def listar_vehiculos(session: AsyncSession = Depends(get_session)):
    return await obtener_vehiculos_db(session)

@app.delete("/vehiculos/{vehiculo_id}", tags=["Vehículos"])
async def eliminar_vehiculo(vehiculo_id: int, session: AsyncSession = Depends(get_session)):
    return await eliminar_vehiculo_db(vehiculo_id, session)

@app.get("/vehiculos/marca/{marca}", response_model=List[VehiculoRead], tags=["Vehículos"])
async def filtrar_por_marca(marca: MarcaVehiculo, session: AsyncSession = Depends(get_session)):
    return await filtrar_vehiculos_por_marca_db(marca, session)

@app.patch("/vehiculos/{vehiculo_id}/form", response_model=VehiculoRead, tags=["Vehículos"])
async def actualizar_vehiculo_formulario(
    vehiculo_id: int,
    vehiculo_update: VehiculoUpdateForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    return await actualizar_vehiculo_db_form(vehiculo_id, vehiculo_update, session)

@app.post("/baterias", response_model=BateriaRead, status_code=status.HTTP_201_CREATED, tags=["Baterías"])
async def crear_bateria(bateria_create: BateriaCreateForm = Depends(), session: AsyncSession = Depends(get_session)):
    return await crear_bateria_db(bateria_create, session)

@app.get("/baterias", response_model=List[BateriaRead], tags=["Baterías"])
async def listar_baterias(session: AsyncSession = Depends(get_session)):
    return await obtener_baterias_db(session)

@app.delete("/baterias/{bateria_id}", tags=["Baterías"])
async def eliminar_bateria(bateria_id: int, session: AsyncSession = Depends(get_session)):
    return await eliminar_bateria_db(bateria_id, session)

@app.patch("/baterias/{bateria_id}", response_model=BateriaRead, tags=["Baterías"])
async def actualizar_bateria(
    bateria_id: int,
    bateria_update: BateriaUpdateForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    return await actualizar_bateria_db(bateria_id, bateria_update, session)

@app.post("/baterias/{bateria_id}/asociar", response_model=BateriaRead, tags=["Operaciones vehículo-Batería"])
async def asociar_bateria_a_vehiculo(
    bateria_id: int,
    vehiculo_id: int = Form(...),
    session: AsyncSession = Depends(get_session),
):
    return await asociar_bateria_a_vehiculo_db(bateria_id, vehiculo_id, session)

@app.get("/dashboard", tags=["Operaciones vehículo-Batería"])
async def dashboard_metrica(session: AsyncSession = Depends(get_session)):
    return await obtener_dashboard_metricas(session)

@app.get("/vehiculos/con-bateria", response_model=List[VehiculoRead], tags=["Vehículos"])
async def listar_vehiculos_con_bateria(session: AsyncSession = Depends(get_session)):
    return await obtener_vehiculos_con_bateria(session)

@app.get("/vehiculos/sin-bateria", response_model=List[VehiculoRead], tags=["Vehículos"])
async def listar_vehiculos_sin_bateria(session: AsyncSession = Depends(get_session)):
    return await obtener_vehiculos_sin_bateria(session)