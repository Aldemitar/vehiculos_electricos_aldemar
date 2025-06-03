from contextlib import asynccontextmanager
from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd

from data.schemas import VehiculoCreate, VehiculoRead, VehiculoCreateForm
from operations.operations_db import crear_vehiculo_db

from utils.connection_db import init_db, get_session
from utils.supabase_db import save_file

from data.models import Vehiculo, Bateria
from data.schemas import VehiculoCreateForm, VehiculoRead, VehiculoCreate, VehiculoUpdateForm, BateriaCreateForm, BateriaRead, BateriaUpdateForm
from data.enums import MarcaVehiculo

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy import func

from typing import List, Optional

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
    return templates.TemplateResponse("add_vehicle.html", {"request": request, "marcas": list(MarcaVehiculo), "titulo": "Creación vehículo"})

@router.post("/vehiculos/add", status_code=status.HTTP_303_SEE_OTHER, tags=["Vehículos"])
async def submit_vehiculo_form(
    vehiculo_form: VehiculoCreateForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    imagen_url = None

    if vehiculo_form.imagen:
        resultado = await save_file(vehiculo_form.imagen, to_supabase=True)

        if "url" in resultado:
            imagen_url = resultado["url"]
        else:
            print("Error al subir imagen:", resultado.get("error"))

    vehiculo_create = VehiculoCreate(
        marca=vehiculo_form.marca,
        modelo=vehiculo_form.modelo,
        año=vehiculo_form.año,
        imagen_url=imagen_url,
    )
    await crear_vehiculo_db(vehiculo_create, session)
    return RedirectResponse(url="/vehiculos_registro", status_code=status.HTTP_303_SEE_OTHER)

@router.delete("/vehiculos/{vehiculo_id}", tags=["Vehículos"])
async def eliminar_vehiculo(vehiculo_id: int, session: AsyncSession = Depends(get_session)):
    return await eliminar_vehiculo_db(vehiculo_id, session)

@router.post("/vehiculos/delete/{vehiculo_id}", tags=["Vehículos"])
async def eliminar_vehiculo_form(vehiculo_id: int, session: AsyncSession = Depends(get_session)):
    await eliminar_vehiculo_db(vehiculo_id, session)
    return RedirectResponse(url="/vehiculos_registro", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/vehiculos_eliminados", response_class=HTMLResponse, tags=["Vehículos"])
async def vehiculos_eliminados_html(request: Request, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Vehiculo).where(Vehiculo.eliminado == True))
    vehiculos = result.scalars().all()
    return templates.TemplateResponse("vehiculos_eliminados.html", {
        "request": request,
        "sesiones": vehiculos,
        "titulo": "Vehículos eliminados"
    })

@router.post("/vehiculos/restaurar/{vehiculo_id}", tags=["Vehículos"])
async def restaurar_vehiculo(vehiculo_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Vehiculo).where(Vehiculo.id == vehiculo_id))
    vehiculo = result.scalar_one_or_none()

    if vehiculo is None or vehiculo.eliminado is False:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado o ya está activo.")

    vehiculo.eliminado = False
    await session.commit()
    return RedirectResponse(url="/vehiculos_registro", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/vehiculos/edit/{vehiculo_id}", tags=["Vehículos"])
async def editar_vehiculo_form(request: Request, vehiculo_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Vehiculo).where(Vehiculo.id == vehiculo_id))
    vehiculo = result.scalar_one_or_none()
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    return templates.TemplateResponse("edit_vehicle.html",{
            "request": request,
            "vehiculo": vehiculo,
            "marcas": MarcaVehiculo,
            "imagen_url": vehiculo.imagen_url
        }
    )

@router.post("/vehiculos/update/{vehiculo_id}", tags=["Vehículos"])
async def actualizar_vehiculo_post(
    vehiculo_id: int,
    vehiculo_update: VehiculoUpdateForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    vehiculo = await actualizar_vehiculo_db_form(vehiculo_id, vehiculo_update, session)
    return RedirectResponse(url="/vehiculos_registro", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/vehiculos", response_class=HTMLResponse, tags=["Vehículos"])
async def vista_vehiculos_html(
    request: Request,
    marca: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    if marca:
        try:
            marca_enum = MarcaVehiculo(marca)
            vehiculos = await filtrar_vehiculos_por_marca_db(marca_enum, session)
            titulo = f"Vehículos - Marca: {marca}"
        except ValueError:
            vehiculos = []
            titulo = "Marca no válida"
    else:
        vehiculos = await obtener_vehiculos_db(session)
        titulo = "Vehículos registrados"
    
    return templates.TemplateResponse("vehiculos_registro.html", {
        "request": request,
        "sesiones": vehiculos,
        "titulo": titulo,
        "marca_seleccionada": marca
    })

@router.get("/baterias/add", tags=["Baterías"])
async def form_agregar_bateria(request: Request):
    return templates.TemplateResponse("add_bateria.html", {"request": request, "titulo": "Creación Batería"})

@router.post("/baterias/add", tags=["Baterías"])
async def procesar_formulario_bateria(
    bateria_form: BateriaCreateForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    await crear_bateria_db(bateria_form, session)
    return RedirectResponse(url="/baterias", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/baterias/delete/{bateria_id}", tags=["Baterías"])
async def eliminar_bateria_form(bateria_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Bateria).where(Bateria.id == bateria_id))
    bateria = result.scalar_one_or_none()

    if bateria is None:
        raise HTTPException(status_code=404, detail="Batería no encontrada")

    bateria.eliminado = True
    await session.commit()
    
    return RedirectResponse(url="/baterias", status_code=303)

@router.post("/baterias/restaurar/{bateria_id}")
async def restaurar_bateria(bateria_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Bateria).where(Bateria.id == bateria_id))
    bateria = result.scalar_one_or_none()

    if not bateria:
        raise HTTPException(status_code=404, detail="Batería no encontrada")

    bateria.eliminado = False
    await session.commit()
    return RedirectResponse(url="/baterias", status_code=303)

@router.get("/baterias/eliminadas", response_class=HTMLResponse)
async def baterias_eliminadas_html(request: Request, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Bateria).where(Bateria.eliminado == True))
    baterias = result.scalars().all()
    return templates.TemplateResponse("baterias_eliminadas.html", {
        "request": request,
        "baterias": baterias,
        "titulo": "Baterías eliminadas"
    })

@router.get("/baterias/edit/{bateria_id}", tags=["Baterías"])
async def form_editar_bateria(bateria_id: int, request: Request, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Bateria).where(Bateria.id == bateria_id))
    bateria = result.scalar_one_or_none()

    if bateria is None:
        raise HTTPException(status_code=404, detail="Batería no encontrada")

    return templates.TemplateResponse("edit_bateria.html", {
        "request": request,
        "bateria": bateria
    })

@router.post("/baterias/update/{bateria_id}", tags=["Baterías"])
async def actualizar_bateria_form(
    bateria_id: int,
    bateria_update: BateriaUpdateForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    await actualizar_bateria_db(bateria_id, bateria_update, session)
    return RedirectResponse(url="/baterias_registro", status_code=303)

@router.get("/baterias", response_class=HTMLResponse)
async def mostrar_baterias(
    request: Request,
    session: AsyncSession = Depends(get_session),
    asignada: Optional[str] = None
):
    query = select(Bateria).where(Bateria.eliminado == False)
    if asignada == "true":
        query = query.where(Bateria.vehiculo_id.is_not(None))
    elif asignada == "false":
        query = query.where(Bateria.vehiculo_id.is_(None))

    result = await session.execute(query)
    baterias = result.scalars().all()

    vehiculos_disponibles = await obtener_vehiculos_sin_bateria(session)
    return templates.TemplateResponse("baterias_registro.html", {
        "request": request,
        "titulo": "Baterías registradas",
        "baterias": baterias,
        "asignada": asignada,
        "vehiculos_disponibles": vehiculos_disponibles
    })

@router.post("/baterias/{bateria_id}/asociar", tags=["Operaciones vehículo-Batería"])
async def asociar_bateria_a_vehiculo(
    bateria_id: int,
    vehiculo_id: int = Form(...),
    session: AsyncSession = Depends(get_session),
):
    await asociar_bateria_a_vehiculo_db(bateria_id, vehiculo_id, session)
    return RedirectResponse(url="/baterias", status_code=303)

@router.post("/baterias/{bateria_id}/desasociar")
async def desasociar_bateria(bateria_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Bateria).where(Bateria.id == bateria_id))
    bateria = result.scalar_one_or_none()
    if not bateria:
        raise HTTPException(status_code=404, detail="Batería no encontrada")
    bateria.vehiculo_id = None
    await session.commit()
    return RedirectResponse(url="/baterias", status_code=303)

@router.get("/estadisticas", response_class=HTMLResponse)
async def estadisticas(request: Request, session: AsyncSession = Depends(get_session)):
    baterias_result = await session.execute(select(Bateria).where(Bateria.eliminado == False))
    baterias = baterias_result.scalars().all()

    vehiculos_result = await session.execute(select(Vehiculo).where(Vehiculo.eliminado == False))
    vehiculos = vehiculos_result.scalars().all()

    total_baterias = len(baterias)
    total_vehiculos = len(vehiculos)

    baterias_asignadas = sum(1 for b in baterias if b.vehiculo_id)
    baterias_no_asignadas = total_baterias - baterias_asignadas

    avg_salud = round(sum(b.estado_salud for b in baterias) / total_baterias, 2) if total_baterias > 0 else 0

    asignacion_labels = ["Asignadas", "No asignadas"]
    asignacion_data = [baterias_asignadas, baterias_no_asignadas]

    marca_counts = {}
    for v in vehiculos:
        marca_counts[v.marca] = marca_counts.get(v.marca, 0) + 1
    marcas_labels = list(marca_counts.keys())
    marcas_data = list(marca_counts.values())

    estado_salud_counts = {"Buen estado": 0, "Regular": 0, "Mal estado": 0}
    for b in baterias:
        if b.estado_salud >= 80:
            estado_salud_counts["Buen estado"] += 1
        elif b.estado_salud >= 50:
            estado_salud_counts["Regular"] += 1
        else:
            estado_salud_counts["Mal estado"] += 1

    salud_labels = list(estado_salud_counts.keys())
    salud_data = list(estado_salud_counts.values())

    return templates.TemplateResponse("estadisticas.html", {
        "request": request,
        "titulo": "Estadísticas Generales",
        "total_baterias": total_baterias,
        "total_vehiculos": total_vehiculos,
        "avg_salud": avg_salud,
        "asignacion_labels": asignacion_labels,
        "asignacion_data": asignacion_data,
        "marcas_labels": marcas_labels,
        "marcas_data": marcas_data,
        "salud_labels": salud_labels,
        "salud_data": salud_data,
    })

@router.get("/planeacion", response_class=HTMLResponse)
async def ver_planeacion(request: Request):
    return templates.TemplateResponse("planeacion.html", {"request": request})

@router.get("/diseno", response_class=HTMLResponse)
async def ver_diseno(request: Request):
    return templates.TemplateResponse("diseno.html", {"request": request})

@router.get("/desarrollador", response_class=HTMLResponse)
async def ver_desarrollador(request: Request):
    return templates.TemplateResponse("desarrollador.html", {"request": request})

@router.get("/objetivo", response_class=HTMLResponse)
async def ver_desarrollador(request: Request):
    return templates.TemplateResponse("objetivos.html", {"request": request})