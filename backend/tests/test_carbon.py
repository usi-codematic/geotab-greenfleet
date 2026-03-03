"""Tests for the carbon calculation service."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.carbon_service import (
    estimate_co2_from_fuel,
    estimate_fuel_from_distance,
    estimate_co2_from_distance,
    ev_savings_estimate
)


def test_co2_from_fuel_gasoline():
    co2 = estimate_co2_from_fuel(100, "gasoline")
    assert co2 == 231.0, f"Expected 231.0, got {co2}"


def test_co2_from_fuel_diesel():
    co2 = estimate_co2_from_fuel(100, "diesel")
    assert co2 == 268.0, f"Expected 268.0, got {co2}"


def test_co2_from_fuel_default():
    co2 = estimate_co2_from_fuel(100, "default")
    assert co2 == 250.0, f"Expected 250.0, got {co2}"


def test_fuel_from_distance_default():
    fuel = estimate_fuel_from_distance(1000, "default")
    assert fuel == 120.0, f"Expected 120.0, got {fuel}"


def test_fuel_from_distance_truck():
    fuel = estimate_fuel_from_distance(1000, "truck")
    assert fuel == 150.0, f"Expected 150.0, got {fuel}"


def test_co2_from_distance():
    co2 = estimate_co2_from_distance(1000, "default", "default")
    expected = 1000 * 0.12 * 2.50  # 300 kg
    assert co2 == expected, f"Expected {expected}, got {co2}"


def test_ev_savings():
    result = ev_savings_estimate(
        distance_km=10000,
        fuel_cost_per_liter=1.65,
        elec_cost_per_kwh=0.13
    )
    assert result["fuel_cost"] > result["electricity_cost"]
    assert result["total_savings"] > 0
    assert result["co2_saved_kg"] > 0


if __name__ == "__main__":
    tests = [
        test_co2_from_fuel_gasoline,
        test_co2_from_fuel_diesel,
        test_co2_from_fuel_default,
        test_fuel_from_distance_default,
        test_fuel_from_distance_truck,
        test_co2_from_distance,
        test_ev_savings,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS: {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {t.__name__} - {e}")
        except Exception as e:
            print(f"  ERROR: {t.__name__} - {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
