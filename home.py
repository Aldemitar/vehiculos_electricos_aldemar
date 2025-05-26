from contextlib import asynccontextmanager
from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd

from data.schemas import VehiculoCreate, VehiculoRead, VehiculoCreateForm
from operations.operations_db import crear_vehiculo_db

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
async def lifespan(app: APIRouter):
    await init_db()
    yield

templates = Jinja2Templates(directory="templates")
router = APIRouter(lifespan=lifespan)

@router.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/vehiculos_registro", response_class=HTMLResponse, tags=["Vehículos"])
async def vehiculos_html(request: Request, session: AsyncSession = Depends(get_session)):
    vehiculos = await obtener_vehiculos_db(session)

    return templates.TemplateResponse("vehiculos_registro.html", {
        "request": request,
        "sesiones": vehiculos,
        "titulo": "Vehículos registrados"
    })

@router.get("/vehiculos/add", response_class=HTMLResponse, tags=["Vehículos"])
async def show_vehiculo_form(request: Request):
    return templates.TemplateResponse("add_vehicle.html", {"request": request, "marcas": list(MarcaVehiculo)})

@router.post("/vehiculos/add", status_code=status.HTTP_303_SEE_OTHER, tags=["Vehículos"])
async def submit_vehiculo_form(
    vehiculo_form: VehiculoCreateForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    vehiculo_create = VehiculoCreate(
        marca=vehiculo_form.marca,
        modelo=vehiculo_form.modelo,
        año=vehiculo_form.año,
    )
    nuevo_vehiculo = await crear_vehiculo_db(vehiculo_create, session)
    return RedirectResponse(url="/vehiculos_registro", status_code=status.HTTP_303_SEE_OTHER)

@router.delete("/vehiculos/{vehiculo_id}", tags=["Vehículos"])
async def eliminar_vehiculo(vehiculo_id: int, session: AsyncSession = Depends(get_session)):
    return await eliminar_vehiculo_db(vehiculo_id, session)

@router.post("/vehiculos/delete/{vehiculo_id}", tags=["Vehículos"])
async def eliminar_vehiculo_form(vehiculo_id: int, session: AsyncSession = Depends(get_session)):
    await eliminar_vehiculo_db(vehiculo_id, session)
    return RedirectResponse(url="/vehiculos_registro", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/vehiculos/marca/{marca}", response_model=List[VehiculoRead], tags=["Vehículos"])
async def filtrar_por_marca(marca: MarcaVehiculo, session: AsyncSession = Depends(get_session)):
    return await filtrar_vehiculos_por_marca_db(marca, session)

@router.patch("/vehiculos/{vehiculo_id}/form", response_model=VehiculoRead, tags=["Vehículos"])
async def actualizar_vehiculo_formulario(
    vehiculo_id: int,
    vehiculo_update: VehiculoUpdateForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    return await actualizar_vehiculo_db_form(vehiculo_id, vehiculo_update, session)

@router.post("/baterias", response_model=BateriaRead, status_code=status.HTTP_201_CREATED, tags=["Baterías"])
async def crear_bateria(bateria_create: BateriaCreateForm = Depends(), session: AsyncSession = Depends(get_session)):
    return await crear_bateria_db(bateria_create, session)

@router.get("/baterias", response_model=List[BateriaRead], tags=["Baterías"])
async def listar_baterias(session: AsyncSession = Depends(get_session)):
    return await obtener_baterias_db(session)

@router.delete("/baterias/{bateria_id}", tags=["Baterías"])
async def eliminar_bateria(bateria_id: int, session: AsyncSession = Depends(get_session)):
    return await eliminar_bateria_db(bateria_id, session)

@router.patch("/baterias/{bateria_id}", response_model=BateriaRead, tags=["Baterías"])
async def actualizar_bateria(
    bateria_id: int,
    bateria_update: BateriaUpdateForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    return await actualizar_bateria_db(bateria_id, bateria_update, session)

@router.post("/baterias/{bateria_id}/asociar", response_model=BateriaRead, tags=["Operaciones vehículo-Batería"])
async def asociar_bateria_a_vehiculo(
    bateria_id: int,
    vehiculo_id: int = Form(...),
    session: AsyncSession = Depends(get_session),
):
    return await asociar_bateria_a_vehiculo_db(bateria_id, vehiculo_id, session)

@router.get("/dashboard", tags=["Operaciones vehículo-Batería"])
async def dashboard_metrica(session: AsyncSession = Depends(get_session)):
    return await obtener_dashboard_metricas(session)

@router.get("/vehiculos/con-bateria", response_model=List[VehiculoRead], tags=["Vehículos"])
async def listar_vehiculos_con_bateria(session: AsyncSession = Depends(get_session)):
    return await obtener_vehiculos_con_bateria(session)

@router.get("/vehiculos/sin-bateria", response_model=List[VehiculoRead], tags=["Vehículos"])
async def listar_vehiculos_sin_bateria(session: AsyncSession = Depends(get_session)):
    return await obtener_vehiculos_sin_bateria(session)