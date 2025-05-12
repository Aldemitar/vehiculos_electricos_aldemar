from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from utils.connection_db import init_db, get_session
from data.models import Vehiculo
from data.schemas import VehiculoCreateForm, VehiculoRead
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List
from operations.operations_db import (
    crear_vehiculo_db
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/vehiculos/form", response_model=VehiculoRead, status_code=status.HTTP_201_CREATED, tags=["Vehículos"])
async def crear_vehiculo_form(vehiculo: VehiculoCreateForm = Depends(), session: AsyncSession = Depends(get_session)):
    vehiculo_dict = vehiculo.__dict__
    vehiculo_create = VehiculoCreateForm(**vehiculo_dict)
    return await crear_vehiculo_db(vehiculo_create, session)