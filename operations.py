import csv
from models import *

VEHICLE_DATABASE_FILENAME = "electric_vehicles.csv"
ELECTRICITY_PRICE_DATABASE_FILENAME = "electricity_prices.csv"

vehicle_column_fields = ["id", "brand", "model", "year", "battery_capacity_kwh", "range_km", "charger_type"]
electricity_price_column_fields = ["id", "city", "electricity_type", "electricity_price", "date"]

def get_next_vehicle_id():
    try:
        with open(VEHICLE_DATABASE_FILENAME, mode="r") as csvfile:
            reader = csv.DictReader(csvfile)
            max_id = max(int(row["id"]) for row in reader)
            return max_id + 1
    except (FileNotFoundError, ValueError):
        return 1

def create_new_vehicle(vehicle: ElectricVehicle):
    vehicle_id = get_next_vehicle_id()
    vehicle_with_id = ElectricVehicleWithId(id=vehicle_id, **vehicle.dict())
    save_vehicle_to_csv(vehicle_with_id)
    return vehicle_with_id

def save_vehicle_to_csv(vehicle: ElectricVehicleWithId):
    file_exists = False
    try:
        with open(VEHICLE_DATABASE_FILENAME, mode="r", newline="") as file:
            file_exists = bool(file.readline().strip())
    except FileNotFoundError:
        pass

    with open(VEHICLE_DATABASE_FILENAME, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=vehicle_column_fields)
        if not file_exists:
            writer.writeheader()
        writer.writerow(vehicle.dict())

def read_all_electric_vehicles():
    with open(VEHICLE_DATABASE_FILENAME) as csvfile:
        reader = csv.DictReader(csvfile)
        return [ElectricVehicleWithId(**row) for row in reader]

def filter_electric_vehicles(brand: str = None, year: int = None, charger_type: str = None):
    vehicles = read_all_electric_vehicles()
    filtered_vehicles = []

    for vehicle in vehicles:
        if (brand is None or vehicle.brand.lower() == brand.lower()) and \
           (year is None or vehicle.year == year) and \
           (charger_type is None or vehicle.charger_type.lower() == charger_type.lower()):
            filtered_vehicles.append(vehicle)

    return filtered_vehicles

def search_electric_vehicles_by_criteria(year: int = None, charger_type: str = None):
    vehicles = read_all_electric_vehicles()
    searched_vehicles = []

    for vehicle in vehicles:
        if (year is None or vehicle.year == year) and \
           (charger_type is None or vehicle.charger_type.lower() == charger_type.lower()):
            searched_vehicles.append(vehicle)

    return searched_vehicles

def update_electric_vehicle(brand: str, model: str, vehicle_update: UpdateElectricVehicle):
    vehicles = read_all_electric_vehicles()
    updated_vehicle = None
    vehicle_found = False

    for index, vehicle in enumerate(vehicles):
        if vehicle.brand.lower() == brand.lower() and vehicle.model.lower() == model.lower():
            if vehicle_update.model:
                vehicles[index].model = vehicle_update.model
            if vehicle_update.year:
                vehicles[index].year = vehicle_update.year
            if vehicle_update.battery_capacity_kwh:
                vehicles[index].battery_capacity_kwh = vehicle_update.battery_capacity_kwh
            if vehicle_update.range_km:
                vehicles[index].range_km = vehicle_update.range_km
            if vehicle_update.charger_type:
                vehicles[index].charger_type = vehicle_update.charger_type

            updated_vehicle = vehicles[index]
            vehicle_found = True
            break

    if not vehicle_found:
        return None

    with open(VEHICLE_DATABASE_FILENAME, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=vehicle_column_fields)
        writer.writeheader()
        for vehicle in vehicles:
            writer.writerow(vehicle.dict())

    return updated_vehicle

def delete_electric_vehicle(brand: str, model: str):
    vehicles = read_all_electric_vehicles()
    updated_vehicles = [
        vehicle for vehicle in vehicles if not (vehicle.brand.lower() == brand.lower() and vehicle.model.lower() == model.lower())
    ]
    if len(updated_vehicles) == len(vehicles):
        return None

    for index, vehicle in enumerate(updated_vehicles, start=1):
        vehicle.id = index

    with open(VEHICLE_DATABASE_FILENAME, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=vehicle_column_fields)
        writer.writeheader()
        for vehicle in updated_vehicles:
            writer.writerow(vehicle.dict())

    return VehicleWithBrand(brand=brand, model=model)

def get_next_electricity_price_id():
    try:
        with open(ELECTRICITY_PRICE_DATABASE_FILENAME, mode="r") as csvfile:
            reader = csv.DictReader(csvfile)
            max_id = max(int(row["id"]) for row in reader)
            return max_id + 1
    except (FileNotFoundError, ValueError):
        return 1

def create_new_electricity_price(price: ElectricityPrice):
    price_id = get_next_electricity_price_id()
    price_with_id = ElectricityPriceWithId(id=price_id, **price.dict())
    save_electricity_price_to_csv(price_with_id)
    return price_with_id

def save_electricity_price_to_csv(price: ElectricityPriceWithId):
    file_exists = False
    try:
        with open(ELECTRICITY_PRICE_DATABASE_FILENAME, mode="r", newline="") as file:
            file_exists = bool(file.readline().strip())
    except FileNotFoundError:
        pass

    with open(ELECTRICITY_PRICE_DATABASE_FILENAME, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=electricity_price_column_fields)
        if not file_exists:
            writer.writeheader()
        writer.writerow(price.dict())

def read_all_electricity_prices():
    with open(ELECTRICITY_PRICE_DATABASE_FILENAME) as csvfile:
        reader = csv.DictReader(csvfile)
        return [ElectricityPriceWithId(**row) for row in reader]

def update_electricity_price(city: str, electricity_type: str, price_update: UpdateElectricityPrice):
    prices = read_all_electricity_prices()
    updated_price = None
    price_found = False

    for index, price in enumerate(prices):
        if price.city.lower() == city.lower() and price.electricity_type.lower() == electricity_type.lower():
            if price_update.electricity_price:
                prices[index].electricity_price = price_update.electricity_price
            if price_update.electricity_type:
                prices[index].electricity_type = price_update.electricity_type
            if price_update.date:
                prices[index].date = price_update.date

            updated_price = prices[index]
            price_found = True
            break

    if not price_found:
        return None

    with open(ELECTRICITY_PRICE_DATABASE_FILENAME, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=electricity_price_column_fields)
        writer.writeheader()
        for price in prices:
            writer.writerow(price.dict())

    return updated_price

def delete_electricity_price(city: str, electricity_type: str):
    prices = read_all_electricity_prices()
    updated_prices = [
        price for price in prices if not (price.city.lower() == city.lower() and price.electricity_type.lower() == electricity_type.lower())
    ]
    if len(updated_prices) == len(prices):
        return None

    for index, price in enumerate(updated_prices, start=1):
        price.id = index

    with open(ELECTRICITY_PRICE_DATABASE_FILENAME, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=electricity_price_column_fields)
        writer.writeheader()
        for price in updated_prices:
            writer.writerow(price.dict())

    return DeleteElectricityPrice(city=city,electricity_type=electricity_type)
