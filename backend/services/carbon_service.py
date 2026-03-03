"""
Carbon emissions calculation service.
Provides fleet-level and vehicle-level CO2 estimation.
"""

# Emission factors (kg CO2 per liter)
EMISSION_FACTORS = {
    "gasoline": 2.31,
    "diesel": 2.68,
    "lpg": 1.51,
    "cng": 2.75,
    "default": 2.50
}

# Average fuel consumption by vehicle type (L/100km)
AVG_CONSUMPTION = {
    "car": 8.0,
    "van": 10.0,
    "truck": 15.0,
    "bus": 25.0,
    "default": 12.0
}


def estimate_co2_from_fuel(fuel_liters, fuel_type="default"):
    """Estimate CO2 emissions from fuel consumed."""
    factor = EMISSION_FACTORS.get(fuel_type, EMISSION_FACTORS["default"])
    return fuel_liters * factor


def estimate_fuel_from_distance(distance_km, vehicle_type="default"):
    """Estimate fuel consumed from distance driven."""
    consumption = AVG_CONSUMPTION.get(vehicle_type, AVG_CONSUMPTION["default"])
    return distance_km * consumption / 100


def estimate_co2_from_distance(distance_km, vehicle_type="default", fuel_type="default"):
    """Estimate CO2 from distance (convenience function)."""
    fuel = estimate_fuel_from_distance(distance_km, vehicle_type)
    return estimate_co2_from_fuel(fuel, fuel_type)


def ev_savings_estimate(distance_km, fuel_cost_per_liter=1.65, elec_cost_per_kwh=0.13,
                        ev_efficiency_kwh_per_km=0.2, vehicle_type="default", fuel_type="default"):
    """Calculate annual savings from converting a vehicle to EV."""
    fuel_l = estimate_fuel_from_distance(distance_km, vehicle_type)
    fuel_cost = fuel_l * fuel_cost_per_liter
    elec_cost = distance_km * ev_efficiency_kwh_per_km * elec_cost_per_kwh
    co2_saved = estimate_co2_from_fuel(fuel_l, fuel_type)
    maintenance_savings = 1200  # $/year avg

    return {
        "fuel_cost": fuel_cost,
        "electricity_cost": elec_cost,
        "fuel_savings": fuel_cost - elec_cost,
        "maintenance_savings": maintenance_savings,
        "total_savings": fuel_cost - elec_cost + maintenance_savings,
        "co2_saved_kg": co2_saved,
    }
