from fastapi import FastAPI
from models import Vehiculo, Bateria
from vehiculos_electricos_aldemar.operations.operations_db import crear_vehiculo_con_bateria, obtener_vehiculos
from database import init_db

app = FastAPI(title="API Vehículos Eléctricos")

init_db()

@app.post("/vehiculos/")
def crear_vehiculo(vehiculo: Vehiculo, bateria: Bateria):
    return crear_vehiculo_con_bateria(vehiculo, bateria)

@app.get("/vehiculos/")
def listar_vehiculos():
    return obtener_vehiculos()