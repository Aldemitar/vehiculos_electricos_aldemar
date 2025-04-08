from fastapi import FastAPI, HTTPException
from typing import List
from operations import *
from models import *

app = FastAPI()

@app.post("/electric-vehicles/", response_model=ElectricVehicleWithId)
async def create_electric_vehicle(vehicle: ElectricVehicle):
    return create_new_vehicle(vehicle)

@app.get("/electric-vehicles/", response_model=List[ElectricVehicleWithId])
async def get_all_electric_vehicles():
    return read_all_electric_vehicles()

@app.get("/electric-vehicles/filtered/", response_model=List[ElectricVehicleWithId])
async def get_filtered_electric_vehicles(brand: str = None, year: int = None, charger_type: str = None):
    return filter_electric_vehicles(brand, year, charger_type)

@app.get("/electric-vehicles/search/", response_model=List[ElectricVehicleWithId])
async def search_electric_vehicles(year: int = None, charger_type: str = None):
    return search_electric_vehicles_by_criteria(year, charger_type)

@app.put("/electric-vehicles/{brand}/{model}", response_model=ElectricVehicleWithId)
async def update_electric_vehicle(brand: str, model: str, vehicle_update: UpdateElectricVehicle):
    updated_vehicle = update_electric_vehicle(brand, model, vehicle_update)
    if updated_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehículo eléctrico no encontrado")
    return updated_vehicle

@app.delete("/electric-vehicles/{brand}/{model}", response_model=VehicleWithBrand)
async def delete_electric_vehicle(brand: str, model: str):
    deleted_vehicle = delete_electric_vehicle(brand, model)
    if deleted_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehículo eléctrico no encontrado")
    return deleted_vehicle

@app.post("/electricity-prices/", response_model=ElectricityPriceWithId)
async def create_electricity_price(price: ElectricityPrice):
    return create_new_electricity_price(price)

@app.get("/electricity-prices/", response_model=List[ElectricityPriceWithId])
async def get_all_electricity_prices():
    return read_all_electricity_prices()

@app.put("/electricity-prices/{city}/{electricity_type}", response_model=ElectricityPriceWithId)
async def update_electricity_price(city: str, electricity_type: str, price_update: UpdateElectricityPrice):
    updated_price = update_electricity_price(city, electricity_type, price_update)
    if updated_price is None:
        raise HTTPException(status_code=404, detail="Precio de electricidad no encontrado")
    return updated_price

@app.delete("/electricity-prices/{city}/{electricity_type}", response_model=ElectricityPrice)
async def delete_electricity_price(city: str, electricity_type: str):
    deleted_price = delete_electricity_price(city, electricity_type)
    if deleted_price is None:
        raise HTTPException(status_code=404, detail="Precio de electricidad no encontrado")
    return deleted_price
