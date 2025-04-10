from pydantic import BaseModel
from typing import Optional

class ElectricVehicle(BaseModel):
    brand: str
    model: str
    year: int
    battery_capacity_kwh: float
    range_km: float
    charger_type: str

class ElectricVehicleWithId(ElectricVehicle):
    id: int

class UpdateElectricVehicle(BaseModel):
    model: Optional[str] = None
    year: Optional[int] = None
    battery_capacity_kwh: Optional[float] = None
    range_km: Optional[float] = None
    charger_type: Optional[str] = None

class VehicleWithBrand(BaseModel):
    brand: str
    model: str

class ElectricityPrice(BaseModel):
    city: str
    electricity_type: str
    electricity_price: float
    date: str

class ElectricityPriceWithId(ElectricityPrice):
    id: int

class UpdateElectricityPrice(BaseModel):
    electricity_type: Optional[str] = None
    electricity_price: Optional[float] = None
    date: Optional[str] = None

class DeleteElectricityPrice(BaseModel):
    city: str
    electricity_type: str