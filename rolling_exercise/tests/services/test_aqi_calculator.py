import pytest

from src.services.aqi_calculator import AqiCalculator


@pytest.mark.parametrize(
    ("pm25", "expected_level"),
    [
        (5, "Good"),
        (20, "Moderate"),
        (40, "Unhealthy for Sensitive Groups"),
        (100, "Unhealthy"),
        (200, "Very Unhealthy"),
        (300, "Hazardous"),
    ],
)
def test_pm25_range_decides_the_level(pm25, expected_level):
    result = AqiCalculator().calculate(pm25=pm25, no2=10, co2=1)

    assert result.aqi_level == expected_level


def test_pm25_at_top_of_good_range_gives_top_good_aqi():
    result = AqiCalculator().calculate(pm25=12, no2=10, co2=1)

    assert result.aqi == 50
    assert result.aqi_level == "Good"


def test_highest_pollutant_decides_the_aqi():
    result = AqiCalculator().calculate(pm25=5, no2=700, co2=1)

    assert result.aqi_level == "Very Unhealthy"


def test_co2_above_highest_breakpoint_gives_max_aqi():
    result = AqiCalculator().calculate(pm25=5, no2=10, co2=450)

    assert result.aqi == 500
    assert result.aqi_level == "Hazardous"
