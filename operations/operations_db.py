from sqlmodel import Session, select
from models import Vehiculo, Bateria
from utils.connection_db import engine

def crear_vehiculo_con_bateria(vehiculo: Vehiculo, bateria: Bateria):
    with Session(engine) as session:
        session.add(vehiculo)
        session.flush()
        bateria.vehiculo_id = vehiculo.id
        session.add(bateria)
        session.commit()
        session.refresh(vehiculo)
        return vehiculo

def obtener_vehiculos():
    with Session(engine) as session:
        return session.exec(select(Vehiculo)).all()
